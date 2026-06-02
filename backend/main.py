import os
import shutil
import tempfile
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import google.generativeai as genai

from backend import config
from backend.ingestion import ingest_documents
from backend.retrieval import PersonaRetriever
from backend.prompt_builder import PromptBuilder
from backend.llm import LLMManager
from backend.memory import ConversationMemory
from backend.tts import TTSManager

app = FastAPI(title="Agentic AI Voice Persona")

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize application modules
retriever = None
llm_manager = None
memory_manager = None
tts_manager = None

@app.on_event("startup")
def startup_event():
    global retriever, llm_manager, memory_manager, tts_manager
    
    if not config.GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY environment variable is missing.")
        return
        
    genai.configure(api_key=config.GEMINI_API_KEY)
    llm_manager = LLMManager()
    memory_manager = ConversationMemory()
    tts_manager = TTSManager()
    
    # Check if vector index exists; if not, automatically ingest
    index_path = Path(config.VECTOR_STORE_DIR)
    if not (index_path / "index.faiss").exists():
        print("FAISS index not found. Initiating auto-ingestion on startup...")
        try:
            ingest_documents()
        except Exception as e:
            print(f"Auto-ingestion failed on startup: {e}")
            
    # Initialize retriever
    retriever = PersonaRetriever()

# Models
class ChatRequest(BaseModel):
    query: str
    session_id: str = "default_session"

class ChatResponse(BaseModel):
    response: str
    audio_url: str
    transcript: str

@app.post("/api/ingest")
def trigger_ingestion():
    """
    Manually triggers indexing of files in the knowledge_base folder.
    """
    try:
        success = ingest_documents()
        if success:
            if retriever:
                retriever.load_index()
            return {"status": "success", "message": "Knowledge base indexed successfully."}
        else:
            raise HTTPException(status_code=500, detail="Ingestion completed with errors.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transcribe")
def transcribe_audio(file: UploadFile = File(...)):
    """
    Endpoint to receive audio binary uploads and transcribe them using Google Gemini multimodal audio.
    """
    if not config.GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API Key not configured.")
        
    # Check file extension or content type
    temp_file_path = None
    try:
        # Create a temporary file to save the uploaded audio
        suffix = Path(file.filename).suffix if file.filename else ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
            
        # Determine mime type for Gemini
        mime_type = "audio/wav"
        if suffix == ".webm":
            mime_type = "audio/webm"
        elif suffix == ".mp3":
            mime_type = "audio/mp3"
        elif suffix == ".m4a":
            mime_type = "audio/m4a"
            
        with open(temp_file_path, "rb") as audio_file:
            audio_bytes = audio_file.read()
            
        # Call Gemini model
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content([
            {
                "mime_type": mime_type,
                "data": audio_bytes
            },
            "Transcribe this audio file exactly as spoken. Do not add any introductory or concluding text, explanations, or formatting. Return ONLY the raw transcription text."
        ])
        
        transcript_text = response.text.strip()
        print(f"Gemini Audio Transcription: '{transcript_text}'")
        return {"transcript": transcript_text}
        
    except Exception as e:
        print(f"Error during audio transcription: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
        
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest, background_tasks: BackgroundTasks):
    """
    Receives user text, retrieves relevant context from the FAISS database,
    constructs the prompt, calls GPT-4o-mini, synthesizes response text to audio,
    and returns both the text response and the URL of the synthesized audio file.
    """
    global retriever, llm_manager, memory_manager, tts_manager
    if not (retriever and llm_manager and memory_manager and tts_manager):
        raise HTTPException(status_code=500, detail="Server modules not fully initialized. Check API Key.")

    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        # 1. Vector Search (RAG)
        retrieved_docs = retriever.retrieve(query, k=3)
        
        # 2. Prompt Construction
        system_prompt = PromptBuilder.build_system_prompt(retrieved_docs)
        
        # 3. Retrieve Session History
        history = memory_manager.get_history(request.session_id)
        
        # 4. GPT Response Generation
        ai_response = llm_manager.generate_response(system_prompt, history, query)
        
        # 5. Save turn in conversation memory
        memory_manager.add_message(request.session_id, "user", query)
        memory_manager.add_message(request.session_id, "assistant", ai_response)
        
        # 6. Text-to-Speech Generation
        audio_filename = tts_manager.generate_speech(ai_response)
        audio_url = f"/audio/{audio_filename}"
        
        # Queue old audio cleanup in the background to avoid blocking response
        background_tasks.add_task(tts_manager.cleanup_old_audio)
        
        return ChatResponse(
            response=ai_response,
            audio_url=audio_url,
            transcript=query
        )
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class ClearRequest(BaseModel):
    session_id: str

@app.post("/api/clear")
def clear_memory_endpoint(request: ClearRequest):
    """
    Clears the conversation history for a given session.
    """
    global memory_manager
    if not memory_manager:
        raise HTTPException(status_code=500, detail="Memory manager not initialized.")
    memory_manager.clear_history(request.session_id)
    return {"status": "success", "message": "Conversation history cleared."}

# Mount static audio files route
app.mount("/audio", StaticFiles(directory=str(config.AUDIO_OUTPUT_DIR)), name="audio")

# Mount frontend files at the root level
frontend_dir = config.BASE_DIR / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
else:
    print("WARNING: 'frontend' directory not found. Frontend files will not be served.")

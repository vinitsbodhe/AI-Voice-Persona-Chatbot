import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Directory Paths
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
VECTOR_STORE_DIR = BASE_DIR / "faiss_index"
AUDIO_OUTPUT_DIR = BASE_DIR / "temp_audio"

# Ensure directories exist
VECTOR_STORE_DIR.mkdir(exist_ok=True)
AUDIO_OUTPUT_DIR.mkdir(exist_ok=True)

# Model Definitions
EMBEDDING_MODEL = "models/gemini-embedding-001"
LLM_MODEL = "gemini-2.5-flash"
TTS_LANG = "en"
TTS_TLD = "com"  # 'com' for US accent, 'co.uk' for UK, 'ca' for Canada

# Memory Settings
MEMORY_WINDOW_SIZE = 5  # Retain last 5 conversation turns

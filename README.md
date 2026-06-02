# AI Voice Persona Chatbot

An AI-powered Voice Persona Chatbot that acts as a digital representation of me by answering questions based on my personal background, experiences, strengths, goals, and projects.

The project combines Retrieval-Augmented Generation (RAG), vector search, conversational memory, and voice interaction to create a personalised conversational experience.

---

## Live Demo

Frontend Application:

[https://ai-voice-persona-chatbot.onrender.com/](https://ai-voice-persona-chatbot.onrender.com/)

---

## Features

* Voice-based interaction
* Retrieval-Augmented Generation (RAG)
* Personalised responses from a custom knowledge base
* Conversational memory
* Semantic search using FAISS
* Gemini-powered response generation
* Text-to-Speech output
* Interactive web interface

---

# System Architecture

```text
User Voice Input
        │
        ▼
Speech-to-Text
        │
        ▼
User Query
        │
        ▼
RAG Retrieval
        │
        ▼
Relevant Context
        │
        ▼
Prompt Construction
        │
        ▼
Gemini LLM
        │
        ▼
Generated Response
        │
        ▼
Text-to-Speech
        │
        ▼
Audio Response
```

---

# Technology Stack

## Backend

* Python
* FastAPI

## AI & Retrieval

* Google Gemini
* LangChain
* FAISS
* Google Embeddings

## Frontend

* HTML
* CSS
* JavaScript

## Voice Processing

* Speech-to-Text
* gTTS (Google Text-to-Speech)

---

# Project Structure

```text
project/
│
├── backend/
│   ├── main.py
│   ├── llm.py
│   ├── retriever.py
│   ├── memory.py
│   └── config.py
│
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
│
├── knowledge_base/
│   ├── personal_profile.txt
│   ├── strengths.txt
│   ├── goals.txt
│   ├── projects.txt
│   └── interview_questions.txt
│
├── faiss_index/
│
├── requirements.txt
│
└── README.md
```

---

# Workflow

## 1. Knowledge Base Creation

Personal information is stored in structured text documents.

Examples:

* Personal background
* Education
* Strengths
* Goals
* Projects
* Interview preparation content

---

## 2. Document Ingestion

Documents are converted into embeddings and stored in a FAISS vector database.

```text
Text Files
    │
    ▼
Chunking
    │
    ▼
Embeddings
    │
    ▼
FAISS Index
```

---

## 3. Retrieval

When a user asks a question, the system retrieves the most relevant information from the knowledge base.

```text
User Query
     │
     ▼
Embedding
     │
     ▼
Similarity Search
     │
     ▼
Relevant Context
```

---

## 4. Prompt Construction

The retrieved context is combined with persona instructions and conversation history.

```text
Persona Instructions
        +
Retrieved Context
        +
Conversation History
        +
User Query
```

---

## 5. Response Generation

The final prompt is sent to Gemini.

```text
Prompt
   │
   ▼
Gemini
   │
   ▼
Response
```

---

## 6. Memory Management

The chatbot maintains conversation history to support contextual and follow-up questions.

```text
Conversation
      │
      ▼
Memory Store
      │
      ▼
Prompt Builder
```

---

## 7. Voice Response

Generated responses are converted into speech.

```text
Generated Text
        │
        ▼
Text-to-Speech
        │
        ▼
Audio Output
```

---

# API Endpoints

## Ingest Knowledge Base

```http
POST /api/ingest
```

Builds or refreshes the FAISS index.

---

## Chat

```http
POST /api/chat
```

Accepts user queries and returns AI-generated responses.

---

## Audio Transcription

```http
POST /api/transcribe
```

Converts voice input into text.

---

## Clear Memory

```http
POST /api/clear
```

Resets conversation history.

---

# RAG Pipeline

```text
Knowledge Base
      │
      ▼
Embeddings
      │
      ▼
FAISS Vector Database
      │
      ▼
User Query
      │
      ▼
Similarity Search
      │
      ▼
Relevant Context
      │
      ▼
Gemini LLM
      │
      ▼
Final Response
```

---

# Future Improvements

* Multi-persona support
* Long-term memory
* User authentication
* Streaming responses
* Advanced voice synthesis
* Cloud vector database integration

---

# Author

**Vinit**

IIT (ISM) Dhanbad

Interested in Data Analytics, Product Thinking, AI Applications, and Problem Solving.

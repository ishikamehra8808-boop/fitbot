# 🏋️ FitBot — AI Fitness Chatbot (RAG + LLM)

A full-stack AI fitness chatbot powered by **Retrieval-Augmented Generation (RAG)** and a **Large Language Model (LLM)**. Ask questions about workouts, nutrition, supplements, recovery, and more — FitBot retrieves relevant knowledge from a curated fitness database and generates accurate, evidence-based responses.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_Store-orange)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-black?logo=openai)

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (HTML/JS)                │
│           Beautiful dark-theme chat interface        │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP / SSE
┌──────────────────────▼──────────────────────────────┐
│                  FastAPI Backend                     │
│                                                     │
│  ┌─────────────┐    ┌──────────────────────────┐   │
│  │  RAG Engine  │    │      LLM Client          │   │
│  │             │    │  (OpenAI / Compatible)    │   │
│  │  Chunker ───┼──► │                          │   │
│  │  Embeddings │    │  System Prompt + Context  │   │
│  │  ChromaDB   │    │  → Streaming Response     │   │
│  └─────────────┘    └──────────────────────────┘   │
│         ▲                                           │
│         │                                           │
│  ┌──────┴──────┐                                   │
│  │ Knowledge   │  7 comprehensive fitness guides    │
│  │ Base (.md)  │  ~115KB of curated content         │
│  └─────────────┘                                   │
└─────────────────────────────────────────────────────┘
```

## Features

- 🤖 **RAG-Powered Responses** — Retrieves relevant fitness knowledge before generating answers
- 📚 **Curated Knowledge Base** — 7 detailed markdown guides covering exercises, nutrition, workout plans, recovery, supplements, cardio, and flexibility
- 🔄 **Real-time Streaming** — Server-Sent Events (SSE) for token-by-token response display
- 💬 **Chat History** — Maintains conversation context across messages
- 📑 **Source Attribution** — Shows which knowledge base documents were used
- 🎨 **Beautiful UI** — Dark-themed, responsive chat interface with animations
- ⚡ **Local Embeddings** — Uses `sentence-transformers` (all-MiniLM-L6-v2) — no API call needed for embeddings
- 🔌 **Flexible LLM Backend** — Works with OpenAI, or any OpenAI-compatible API (Ollama, LM Studio, etc.)

## Quick Start

### 1. Prerequisites

- Python 3.10+
- An OpenAI API key (or a local LLM server)

### 2. Install Dependencies

```bash
cd fitness-chatbot
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-actual-key-here
```

### 4. Run the App

```bash
python -m uvicorn app.main:app --reload --port 8000
```

The app will:
1. Load the fitness knowledge base
2. Chunk documents and generate embeddings
3. Store vectors in ChromaDB (persisted to `./chroma_db`)
4. Start the FastAPI server

Open **http://localhost:8000** in your browser!

### 5. (Optional) Manual Ingestion

If you update the knowledge base files, re-ingest:

```bash
python ingest.py
```

## Using with Local LLMs

FitBot works with any OpenAI-compatible API. To use a local model:

### With Ollama
```env
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=ollama
OPENAI_MODEL=llama3.1
```

### With LM Studio
```env
OPENAI_BASE_URL=http://localhost:1234/v1
OPENAI_API_KEY=lm-studio
OPENAI_MODEL=local-model
```

## Project Structure

```
fitness-chatbot/
├── app/
│   ├── __init__.py
│   ├── config.py              # Settings (from .env)
│   ├── main.py                # FastAPI app & endpoints
│   ├── rag/
│   │   ├── chunker.py         # Document chunking
│   │   ├── vectorstore.py     # ChromaDB vector operations
│   │   └── retriever.py       # RAG retrieval pipeline
│   ├── llm/
│   │   └── chat.py            # LLM client (OpenAI)
│   └── static/
│       └── index.html         # Chat UI
├── knowledge_base/
│   ├── exercises.md           # Exercise guides & form tips
│   ├── nutrition.md           # Macros, meal plans, diets
│   ├── workout_plans.md       # PPL, Upper/Lower, Full Body
│   ├── recovery.md            # Sleep, mobility, injury prevention
│   ├── supplements.md         # Creatine, protein, pre-workout
│   ├── cardio.md              # HIIT, LISS, heart rate zones
│   └── flexibility_mobility.md # Stretching & mobility drills
├── ingest.py                  # Standalone ingestion script
├── requirements.txt
├── .env.example
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves the chat UI |
| `POST` | `/api/chat` | Send a message, get a complete response |
| `POST` | `/api/chat/stream` | Send a message, get a streaming SSE response |
| `GET` | `/api/status` | Check vector store status |
| `POST` | `/api/ingest` | Re-ingest the knowledge base |

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | Your OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | LLM model to use |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | API base URL |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence transformer model |
| `CHUNK_SIZE` | `500` | Characters per document chunk |
| `CHUNK_OVERLAP` | `50` | Overlap between chunks |
| `TOP_K_RESULTS` | `5` | Number of retrieved chunks per query |

## How RAG Works in FitBot

1. **Ingestion** — Markdown documents are split into overlapping chunks, each chunk is embedded using sentence-transformers and stored in ChromaDB
2. **Retrieval** — When a user asks a question, the query is embedded and the top-K most similar chunks are retrieved from ChromaDB
3. **Augmentation** — Retrieved chunks are injected into the LLM prompt as context, with source attribution
4. **Generation** — The LLM generates a response grounded in the retrieved fitness knowledge

## License

MIT

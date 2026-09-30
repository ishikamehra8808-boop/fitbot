from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from contextlib import asynccontextmanager
import os
import json

from app.config import config
from app.rag.retriever import FitnessRetriever
from app.llm.chat import FitnessChat

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []

retriever = None
chat_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global retriever, chat_client
    os.makedirs(config.KNOWLEDGE_BASE_DIR, exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(__file__), "static"), exist_ok=True)
    
    retriever = FitnessRetriever(config)
    chat_client = FitnessChat(config)
    
    if retriever.get_status()["document_count"] == 0:
        print("Knowledge base empty. Ingesting documents...")
        retriever.ingest_knowledge_base()
        
    yield
    print("Shutting down...")

app = FastAPI(title="Fitness Chatbot API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(os.path.join(os.path.dirname(__file__), "static"), exist_ok=True)
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

@app.get("/")
async def root():
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Fitness Chatbot API running"}

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        retrieval = retriever.retrieve(request.message, top_k=config.TOP_K_RESULTS)
        context = retrieval["context"]
        sources = retrieval["sources"]
        
        response = await chat_client.chat(request.message, context, request.history)
        return {"response": response, "sources": sources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    try:
        retrieval = retriever.retrieve(request.message, top_k=config.TOP_K_RESULTS)
        context = retrieval["context"]
        sources = retrieval["sources"]
        
        async def event_generator():
            async for chunk in chat_client.chat_stream(request.message, context, request.history):
                yield f"data: {json.dumps({'text': chunk})}\n\n"
            yield f"data: {json.dumps({'sources': sources})}\n\n"
            yield "data: [DONE]\n\n"
            
        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def status_endpoint():
    return retriever.get_status()

@app.post("/api/ingest")
async def ingest_endpoint():
    try:
        count = retriever.ingest_knowledge_base()
        return {"message": f"Successfully ingested {count} chunks.", "count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

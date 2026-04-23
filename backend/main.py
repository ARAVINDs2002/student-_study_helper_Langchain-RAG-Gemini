import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Run load_dotenv before importing llm/rag as they rely on env vars
load_dotenv()

from llm import invoke_gemini, invoke_rag, add_to_history
from rag import process_document, get_retriever
from utils import parse_llm_json, get_image_urls, generate_flowchart_img

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AskRequest(BaseModel):
    session_id: str
    question: str
    mode: str = "gemini" # "gemini" or "rag"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/upload")
async def upload_file(session_id: str = Form(...), file: UploadFile = File(...)):
    if not file.filename.endswith((".pdf", ".txt")):
        raise HTTPException(status_code=400, detail="Only .pdf and .txt supported")

    chunks_count = await process_document(session_id, file)
    return {"message": "Document processed and RAG enabled", "chunks": chunks_count}

@app.post("/ask")
async def ask_question(request: AskRequest):
    session_id = request.session_id
    question = request.question
    mode = request.mode

    if mode == "rag":
        retriever = get_retriever(session_id)
        if not retriever:
            raise HTTPException(status_code=400, detail="No document loaded for RAG. Please upload first.")
        
        try:
            docs = retriever.invoke(question)
            context = "\n".join([doc.page_content for doc in docs])
            response = invoke_rag(session_id, question, context)
            data = parse_llm_json(response.content)
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                raise HTTPException(status_code=429, detail="API Quota Exceeded. Please wait a few seconds and try again.")
            raise HTTPException(status_code=500, detail=f"LLM/Embedding Error: {str(e)}")
        
        if "not found in document" in data.get("explanation", "").lower() or "not found" in data.get("explanation", "").lower():
            # Fallback
            try:
                response = invoke_gemini(session_id, question)
                data = parse_llm_json(response.content)
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    raise HTTPException(status_code=429, detail="API Quota Exceeded. Please wait a few seconds and try again.")
                raise HTTPException(status_code=500, detail=f"LLM Error: {str(e)}")
    else:
        # Base Gemini
        try:
            response = invoke_gemini(session_id, question)
            data = parse_llm_json(response.content)
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                raise HTTPException(status_code=429, detail="API Quota Exceeded. Please wait a few seconds and try again.")
            raise HTTPException(status_code=500, detail=f"LLM Error: {str(e)}")

    image_urls = get_image_urls(data.get("image_query", ""))
    data["image_urls"] = image_urls
    
    flowchart_img = generate_flowchart_img(data.get("flowchart", ""))
    data["flowchart_img"] = flowchart_img

    # Save to history
    add_to_history(session_id, question, data.get("explanation", ""))

    return JSONResponse(content=data)

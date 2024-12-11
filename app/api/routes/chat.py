from fastapi import APIRouter, HTTPException, UploadFile
from typing import List
from app.services.chat_service import ChatService
from .request_models.chat_request import QuestionRequest

chat_service = ChatService()
router = APIRouter()
@router.post("/generate-warnings")
async def chat():
    try:
        return chat_service.generate_warning()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-chatbot")
async def create_chatbot():
    try:
        return chat_service.create_chatbot()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/ask-latest-chatbot")
async def ask_latest_chatbot(payload: QuestionRequest):
    try:
        return chat_service.ask_latest_chatbot(payload.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/ask-without-faiss")
async def ask_without_faiss(payload: QuestionRequest):
    try:
        return chat_service.ask_without_faiss(payload.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
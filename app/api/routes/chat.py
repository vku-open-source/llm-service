from fastapi import APIRouter, HTTPException, UploadFile
from typing import List
from app.services.chat_service import ChatService

chat_service = ChatService()
router = APIRouter()
@router.post("/generate-warnings")
async def chat():
    try:
        return chat_service.generate_warning()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

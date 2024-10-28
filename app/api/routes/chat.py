from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import List

from app.models import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.api.deps import CurrentUser, SessionDep
from app import crud


router = APIRouter()
chat_service = ChatService()

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    session: SessionDep,
    current_user: CurrentUser
):
    try:
        # Kiểm tra chatbot tồn tại và quyền sở hữu
        chatbot = crud.get_chatbot(session=session, chatbot_id=request.chatbot_id)
        if not chatbot:
            raise HTTPException(status_code=404, detail="Chatbot not found")
        if str(chatbot.owner_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Not enough permissions")

        response = await chat_service.chat(
            message=request.message,
            chatbot_id=str(chatbot.id),  # Chuyển UUID thành string
            session_id=request.session_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

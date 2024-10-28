from typing import Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select
from typing import List
import os
from pathlib import Path
from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.models import (
    ChatbotCreate,
    ChatbotUpdate,
    ChatbotPublic,
    ChatbotsPublic,
    Message
)
from app.services.chat_service import ChatService

router = APIRouter()
chat_service = ChatService()

@router.post("/", response_model=ChatbotPublic)
def create_chatbot(
    *,
    session: SessionDep,
    chatbot_in: ChatbotCreate,
    current_user: CurrentUser,
) -> Any:
    """
    Create new chatbot.
    """
    chatbot = crud.create_chatbot(
        session=session, chatbot_in=chatbot_in, owner_id=str(current_user.id)
    )
    return chatbot

@router.get("/", response_model=ChatbotsPublic)
def read_chatbots(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve chatbots.
    """
    chatbots = crud.get_chatbots_by_owner(
        session=session, owner_id=str(current_user.id), skip=skip, limit=limit
    )
    count = len(chatbots)
    return ChatbotsPublic(data=chatbots, count=count)

@router.get("/{chatbot_id}", response_model=ChatbotPublic)
def read_chatbot(
    *,
    session: SessionDep,
    chatbot_id: str,
    current_user: CurrentUser,
) -> Any:
    """
    Get chatbot by ID.
    """
    chatbot = crud.get_chatbot(session=session, chatbot_id=chatbot_id)
    # print("current user id: ", current_user.id)
    # print("chatbot owner id: ", chatbot.owner_id)
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    if chatbot.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return chatbot

@router.put("/{chatbot_id}", response_model=ChatbotPublic)
def update_chatbot(
    *,
    session: SessionDep,
    chatbot_id: str,
    chatbot_in: ChatbotUpdate,
    current_user: CurrentUser,
) -> Any:
    """
    Update chatbot.
    """
    chatbot = crud.get_chatbot(session=session, chatbot_id=chatbot_id)
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    if chatbot.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    chatbot = crud.update_chatbot(
        session=session, db_obj=chatbot, obj_in=chatbot_in
    )
    return chatbot

@router.delete("/{chatbot_id}", response_model=Message)
def delete_chatbot(
    *,
    session: SessionDep,
    chatbot_id: str,
    current_user: CurrentUser,
) -> Any:
    """
    Delete chatbot.
    """
    chatbot = crud.get_chatbot(session=session, chatbot_id=chatbot_id)
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    if chatbot.owner_id != str(current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    # Delete vector database
    try:
        chat_service.ai_model.delete_vector_db(str(chatbot_id))
    except Exception:
        pass  # Ignore if vector DB doesn't exist
    
    crud.delete_chatbot(session=session, chatbot_id=chatbot_id)
    return Message(message="Chatbot deleted successfully")

@router.post("/train/{chatbot_id}")
async def train_chatbot(
    *,
    session: SessionDep,
    chatbot_id: str,
    current_user: CurrentUser,
    files: List[UploadFile] = File(...),
) -> Any:
    """
    Train chatbot with files.
    """
    chatbot = crud.get_chatbot(session=session, chatbot_id=chatbot_id)
    if not chatbot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    if chatbot.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    try:
        # Tạo thư mục temp nếu chưa tồn tại
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        
        file_data = []
        for file in files:
            content = await file.read()
            file_path = temp_dir / file.filename
            with open(file_path, "wb") as f:
                f.write(content)
            file_data.append({
                "path": str(file_path),
                "type": "csv" if file.filename.endswith(".csv") else "text"
            })
        print("file data: ", file_data) 
        chat_service.ai_model.build_vector_db(str(chatbot_id), file_data)
        
        # Xóa files in temps sau khi đã xử lý xong
        for file_info in file_data:
            try:
                os.remove(file_info["path"])
            except Exception:
                pass
                
        return Message(message="Training completed successfully")
    except Exception as e:
        for file_info in file_data:
            try:
                os.remove(file_info["path"])
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=str(e))
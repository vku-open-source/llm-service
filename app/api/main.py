from fastapi import APIRouter

from app.api.routes import utils, chat, ai

api_router = APIRouter()
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])

api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
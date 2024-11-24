from typing import Optional
import uuid
from app.models import ChatSession, Message, ChatResponse
from app.llm.openai_model import OpenAIModel

class ChatService:
    def __init__(self):
        self._sessions = {}
        self.ai_model = OpenAIModel()

    def _get_or_create_session(self, session_id: Optional[str], chatbot_id: str) -> ChatSession:
        if not session_id or session_id not in self._sessions:
            session_id = str(uuid.uuid4())
            self._sessions[session_id] = ChatSession(
                id=session_id,
                chatbot_id=chatbot_id
            )
        return self._sessions[session_id]

    async def chat(self, message: str, chatbot_id: str, session_id: Optional[str] = None) -> ChatResponse:
        session = self._get_or_create_session(session_id, chatbot_id)

        user_message = Message(content=message, role="user")
        session.messages.append(user_message)

        # Chuyển đổi chat history sang format phù hợp với OpenAI
        chat_history = [
            {"role": msg.role, "content": msg.content} 
            for msg in session.messages[:-1]  
        ]

        # Lấy câu trả lời từ AI với chat history
        try:
            response = self.ai_model.ask_by_chatbot_id(
                chatbot_id, 
                message,
                chat_history=chat_history
            )
        except Exception as e:
            response = {"answer": "Sorry, I'm not trained yet or encountered an error."}
        
        # Lưu câu trả lời của AI
        ai_message = Message(content=response["answer"], role="assistant")
        session.messages.append(ai_message)

        return ChatResponse(
            message=response["answer"],
            session_id=session.id
        )

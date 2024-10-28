import uuid

from pydantic import BaseModel, EmailStr
from sqlmodel import Field, Relationship, SQLModel
from typing import List, Optional
from datetime import datetime
import uuid

# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    chatbots: list["Chatbot"] = Relationship(back_populates="owner", cascade_delete=True)

# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)

# Chatbot model definition
class ChatbotBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    size: str = Field(max_length=50)  # small, medium, large
    color: str = Field(max_length=50)  # primary color hex code
    logo: str | None = Field(default=None, max_length=255)  # URL to logo image
    script: str | None = Field(default=None)  # Link to exported chatbot script

# Properties to receive on chatbot creation
class ChatbotCreate(ChatbotBase):
    pass

# Properties to receive on chatbot update
class ChatbotUpdate(ChatbotBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    size: str | None = Field(default=None, max_length=50)
    color: str | None = Field(default=None, max_length=50)
    logo: str | None = Field(default=None, max_length=255)
    script: str | None = Field(default=None)

# Database model
class Chatbot(ChatbotBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    owner: User | None = Relationship(back_populates="chatbots")

# Properties to return via API
class ChatbotPublic(ChatbotBase):
    id: uuid.UUID
    owner_id: uuid.UUID

class ChatbotsPublic(SQLModel):
    data: list[ChatbotPublic]
    count: int

class Message(BaseModel):
    id: str = str(uuid.uuid4())
    content: str
    role: str  # 'user' or 'assistant'
    timestamp: datetime = datetime.now()

class ChatSession(BaseModel):
    id: str = str(uuid.uuid4())
    messages: List[Message] = []
    chatbot_id: str
    created_at: datetime = datetime.now()
    
class ChatRequest(BaseModel):
    message: str
    chatbot_id: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    session_id: str
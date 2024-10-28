import uuid
from typing import Any, List

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import Item, ItemCreate, User, UserCreate, UserUpdate
from app.models import Chatbot, ChatbotCreate, ChatbotUpdate

def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


# Chatbot CRUD

def create_chatbot(*, session: Session, chatbot_in: ChatbotCreate, owner_id: str) -> Chatbot:
    chatbot = Chatbot(**chatbot_in.model_dump(), owner_id=owner_id)
    session.add(chatbot)
    session.commit()
    session.refresh(chatbot)
    return chatbot

def get_chatbot(*, session: Session, chatbot_id: str) -> Chatbot | None:
    return session.exec(select(Chatbot).where(Chatbot.id == chatbot_id)).first()

def get_chatbots_by_owner(
    *, session: Session, owner_id: str, skip: int = 0, limit: int = 100
) -> List[Chatbot]:
    return session.exec(
        select(Chatbot)
        .where(Chatbot.owner_id == owner_id)
        .offset(skip)
        .limit(limit)
    ).all()

def update_chatbot(
    *, session: Session, db_obj: Chatbot, obj_in: ChatbotUpdate
) -> Chatbot:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def delete_chatbot(*, session: Session, chatbot_id: str) -> Chatbot:
    chatbot = get_chatbot(session=session, chatbot_id=chatbot_id)
    if chatbot:
        session.delete(chatbot)
        session.commit()
    return chatbot
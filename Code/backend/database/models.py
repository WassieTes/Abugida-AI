from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Text,
    DateTime
)

from sqlalchemy.orm import relationship

from datetime import datetime

from .db import Base


# ================= CHAT =================

class Chat(Base):

    __tablename__ = "chats"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String,
        default="New Chat"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # relationships
    messages = relationship(
        "Message",
        back_populates="chat",
        cascade="all, delete"
    )

    documents = relationship(
        "Document",
        back_populates="chat",
        cascade="all, delete"
    )


# ================= MESSAGE =================

class Message(Base):

    __tablename__ = "messages"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    chat_id = Column(
        Integer,
        ForeignKey("chats.id")
    )

    role = Column(String)

    content = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    chat = relationship(
        "Chat",
        back_populates="messages"
    )


# ================= DOCUMENT =================

class Document(Base):

    __tablename__ = "documents"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    chat_id = Column(
        Integer,
        ForeignKey("chats.id"),
        index=True
    )

    filename = Column(
        String,
        index=True
    )

    path = Column(String)

    file_hash = Column(
        String,
        unique=True,
        index=True
    )

    chunk_count = Column(
        Integer,
        default=0
    )

    status = Column(
        String,
        default="active"
    )
    # active | deleted | processing

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    chat = relationship(
        "Chat",
        back_populates="documents"
    )
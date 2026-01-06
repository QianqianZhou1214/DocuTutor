from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
from sqlalchemy.orm import Session
from typing import List

from ..models import ChatHistory


def load_memory_from_db(db: Session, session_id: str, k: int = 10) -> ConversationBufferMemory:
    """
    Load last k chat turns from DB into Langchain Memory
    """

    records: List[ChatHistory] = (
        db.query(ChatHistory)
        .filter(ChatHistory.session_id == session_id)
        .order_by(ChatHistory.timestamp.asc())
        .limit(k * 2)
        .all()
    )

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    for r in records:
        memory.chat_memory.add_user_message(r.question)
        memory.chat_memory.add_ai_message(r.answer)

    return memory

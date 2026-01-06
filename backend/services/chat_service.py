from typing import List, Tuple
from sqlalchemy.orm import Session
from ..models import ChatHistory
import uuid
from datetime import datetime


# new session ID
def new_session() -> str:

    return str(uuid.uuid4())


# add chat history
def add_history(
        session_id: str,
        question: str,
        answer: str,
        db: Session = None,
        user_id: int = None
):
    chat = ChatHistory(session_id=session_id, user_id=user_id, question=question, answer=answer)
    db.add(chat)
    db.commit()


# load chat history from DB
def load_history(
        session_id: str,
        db: Session
) -> List[Tuple[str, str]]:
    chats = db.query(ChatHistory) \
        .filter(ChatHistory.session_id == session_id) \
        .order_by(ChatHistory.timestamp.asc()) \
        .all()

    return [(c.question, c.answer) for c in chats]

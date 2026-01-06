from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from ..models import ChatHistory, User
from sqlalchemy.orm import Session
import uuid

# store session in memory (persistence in DB)
session_histories: Dict[str, List[Tuple[str, str]]] = {}
session_timestamps: Dict[str, datetime] = {}

SESSION_TIMEOUT_HOURS = 2


# new session
def new_session(user_id: int) -> str:
    session_id = str(uuid.uuid4())
    session_histories[session_id] = []
    session_timestamps[session_id] = datetime.now()
    return session_id


# get history
def get_history(session_id: str) -> List[Tuple[str, str]]:
    return session_histories.get(session_id, [])


# add chat history
def add_history(session_id: str, question: str, answer: str, db: Session = None, user_id: int = None):
    if session_id not in session_histories:
        session_histories[session_id] = []
    session_histories[session_id].append((question, answer))
    session_timestamps[session_id] = datetime.now()

    # save to DB
    if db and user_id:
        chat = ChatHistory(session_id=session_id, user_id=user_id, question=question, answer=answer)
        db.add(chat)
        db.commit()


# clean up old sessions
def cleanup_sessions():
    now = datetime.now()
    to_delete = [sid for sid, ts in session_timestamps.items() if now - ts > timedelta(hours=SESSION_TIMEOUT_HOURS)]
    for sid in to_delete:
        session_histories.pop(sid, None)
        session_timestamps.pop(sid, None)

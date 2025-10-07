# app/core/db.py
import os
from typing import Optional, Dict, Any, List
from datetime import datetime

from sqlalchemy import (
    create_engine, Column, String, Integer, Text, TIMESTAMP, func
)
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON as SA_JSON

# Choose JSON type that works both on Postgres and SQLite
def _json_type_from_url(url: str):
    return JSONB if url.startswith("postgresql") else SA_JSON

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///agentwebplus.db")
JSONType = _json_type_from_url(DATABASE_URL)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

# --- Tables ---

class KV(Base):
    __tablename__ = "kv_store"
    key = Column(String(255), primary_key=True)
    value = Column(JSONType)

class MockQA(Base):
    __tablename__ = "mock_qa_history"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), index=True)   # optional session token
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    evaluation = Column(JSONType)                 # {"score":..., "feedback":..., "key_points":[...]}
    created_at = Column(TIMESTAMP, server_default=func.now())

def init_db():
    Base.metadata.create_all(engine)

# --- High-level helpers you can call from Streamlit ---

def save_context_dict(context_dict: Dict[str, Any], key: str = "context") -> None:
    """Upsert entire context dict into KV."""
    with SessionLocal() as s:
        row = s.get(KV, key)
        if row:
            row.value = context_dict
        else:
            row = KV(key=key, value=context_dict)
            s.add(row)
        s.commit()

def load_context_dict(key: str = "context") -> Dict[str, Any]:
    with SessionLocal() as s:
        row = s.get(KV, key)
        return row.value if row and row.value else {}

def log_mock_turn(session_id: str, question: str, answer: str, evaluation: Dict[str, Any]) -> None:
    with SessionLocal() as s:
        rec = MockQA(
            session_id=session_id, question=question, answer=answer, evaluation=evaluation
        )
        s.add(rec)
        s.commit()

def fetch_mock_history(session_id: str) -> List[Dict[str, Any]]:
    with SessionLocal() as s:
        rows = s.query(MockQA).filter(MockQA.session_id == session_id).order_by(MockQA.id).all()
        out = []
        for r in rows:
            out.append({
                "id": r.id,
                "question": r.question,
                "answer": r.answer,
                "evaluation": r.evaluation,
                "created_at": r.created_at.isoformat() if isinstance(r.created_at, datetime) else str(r.created_at)
            })
        return out

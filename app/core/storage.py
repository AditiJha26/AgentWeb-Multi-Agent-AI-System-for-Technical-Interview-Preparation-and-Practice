# app/core/storage.py

import json
from pathlib import Path
from typing import Any, Dict
from app.core.context_store import ContextStore

DEFAULT_PATH = Path("agentwebplus_session.json")

def save_context(ctx: ContextStore, path: Path = DEFAULT_PATH) -> None:
    data: Dict[str, Any] = ctx.get_all()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_context(path: Path = DEFAULT_PATH) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

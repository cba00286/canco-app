"""Persistent long-term memory for the Hermes agent.

Facts accumulate across sessions in a JSON file on disk, so the agent
"remembers more the more it is used" instead of starting from a blank
slate every run.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_MEMORY_PATH = Path(__file__).resolve().parent.parent / "memory" / "memory.json"


class Memory:
    def __init__(self, path: Optional[Path] = None):
        self.path = Path(path) if path else DEFAULT_MEMORY_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.entries: List[Dict[str, Any]] = self._load()

    def _load(self) -> List[Dict[str, Any]]:
        if self.path.exists():
            with self.path.open("r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save(self) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(self.entries, f, ensure_ascii=False, indent=2)

    def remember(self, fact: str, tags: Optional[List[str]] = None) -> Dict[str, Any]:
        entry = {
            "fact": fact,
            "tags": tags or [],
            "created_at": time.time(),
        }
        self.entries.append(entry)
        self._save()
        return entry

    def forget(self, index: int) -> None:
        del self.entries[index]
        self._save()

    def search(self, query: str) -> List[Dict[str, Any]]:
        query_lower = query.lower()
        return [
            e
            for e in self.entries
            if query_lower in e["fact"].lower()
            or any(query_lower in t.lower() for t in e.get("tags", []))
        ]

    def as_context(self, limit: int = 50) -> str:
        if not self.entries:
            return "(기억된 내용 없음)"
        recent = self.entries[-limit:]
        return "\n".join(f"- {e['fact']}" for e in recent)

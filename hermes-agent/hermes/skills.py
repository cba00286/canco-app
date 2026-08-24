"""Skill library: turns repeated task patterns into reusable, replayable skills.

A skill is a named, reusable procedure (a description plus an ordered list
of steps) that the agent learned from a task the user repeated. Once saved,
future requests that match the skill's triggers are recognized and replayed
instead of being solved from scratch every time.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_SKILLS_PATH = Path(__file__).resolve().parent.parent / "skills" / "skills.json"


class SkillLibrary:
    def __init__(self, path: Optional[Path] = None):
        self.path = Path(path) if path else DEFAULT_SKILLS_PATH
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.skills: List[Dict[str, Any]] = self._load()

    def _load(self) -> List[Dict[str, Any]]:
        if self.path.exists():
            with self.path.open("r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save(self) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(self.skills, f, ensure_ascii=False, indent=2)

    def save_skill(
        self,
        name: str,
        description: str,
        steps: List[str],
        triggers: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        existing = self.find_by_name(name)
        if existing:
            existing["description"] = description
            existing["steps"] = steps
            if triggers:
                existing["triggers"] = triggers
            existing["updated_at"] = time.time()
        else:
            existing = {
                "name": name,
                "description": description,
                "steps": steps,
                "triggers": triggers or [name],
                "created_at": time.time(),
                "updated_at": time.time(),
                "usage_count": 0,
            }
            self.skills.append(existing)
        self._save()
        return existing

    def find_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        for s in self.skills:
            if s["name"] == name:
                return s
        return None

    def match(self, user_input: str) -> Optional[Dict[str, Any]]:
        text = user_input.lower()
        best: Optional[Dict[str, Any]] = None
        best_score = 0
        for skill in self.skills:
            triggers = skill.get("triggers") or [skill["name"]]
            score = sum(1 for t in triggers if t.lower() in text)
            if score > best_score:
                best = skill
                best_score = score
        return best

    def mark_used(self, name: str) -> None:
        skill = self.find_by_name(name)
        if skill:
            skill["usage_count"] = skill.get("usage_count", 0) + 1
            skill["last_used_at"] = time.time()
            self._save()

    def as_context(self, limit: int = 20) -> str:
        if not self.skills:
            return "(저장된 스킬 없음)"
        top = sorted(self.skills, key=lambda s: s.get("usage_count", 0), reverse=True)[:limit]
        lines = []
        for s in top:
            triggers = ", ".join(s.get("triggers", [])) or "없음"
            lines.append(
                f"- {s['name']}: {s['description']} (트리거: {triggers}, 사용 {s.get('usage_count', 0)}회)"
            )
        return "\n".join(lines)

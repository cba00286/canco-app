"""Hermes Agent core: a memory-grounded, skill-reusing conversational agent.

Two behaviors distinguish Hermes from a stateless chatbot:

1. Persistent memory (`Memory`) — facts learned in one session are still
   known in the next one, so the agent gets more useful the more it's used.
2. Skill formation (`SkillLibrary`) — when the same kind of request keeps
   coming up, the agent notices the repetition and lets the user save it
   as a named skill; matching future requests are then recognized and
   replayed instead of solved from scratch.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import List, Optional

from .memory import Memory
from .skills import SkillLibrary

SYSTEM_PROMPT_TEMPLATE = """당신은 Hermes라는 이름의 개인화된 AI 에이전트입니다.
사용할수록 사용자에 대해 더 많이 기억하고, 반복되는 작업은 재사용 가능한 스킬로
저장해 다음에는 더 빠르고 정확하게 처리합니다.

# 영구 기억 (지금까지 기억한 것)
{memory_context}

# 보유 스킬 (반복작업이 학습되어 저장된 것)
{skills_context}

사용자의 요청에 답할 때 위 기억과 스킬을 최대한 활용하세요. 새로운 사실을 알게
되면 기억해 두어야 할 내용임을 답변에서 알려주세요.
"""


def normalize(text: str) -> str:
    """Loose normalization used to detect that two requests are "the same task"."""
    text = text.strip().lower()
    text = re.sub(r"[^\w\s가-힣]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


@dataclass
class TaskRecord:
    raw: str
    normalized: str


class HermesAgent:
    """Ties memory + skills + the Claude API together into one agent loop."""

    SKILL_LEARN_THRESHOLD = 2  # this many repeats of the same task triggers a skill-save suggestion

    def __init__(
        self,
        memory: Optional[Memory] = None,
        skills: Optional[SkillLibrary] = None,
        model: str = "claude-sonnet-5",
    ):
        self.memory = memory or Memory()
        self.skills = skills or SkillLibrary()
        self.model = model
        self.history: List[TaskRecord] = []
        self._client = None

    @property
    def client(self):
        if self._client is None:
            import anthropic

            self._client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        return self._client

    def _repeat_count(self, normalized: str) -> int:
        return sum(1 for h in self.history if h.normalized == normalized) + 1

    def observe_task(self, user_input: str) -> int:
        """Record a task and return how many times this same task has now been seen."""
        norm = normalize(user_input)
        count = self._repeat_count(norm)
        self.history.append(TaskRecord(raw=user_input, normalized=norm))
        return count

    def build_system_prompt(self) -> str:
        return SYSTEM_PROMPT_TEMPLATE.format(
            memory_context=self.memory.as_context(),
            skills_context=self.skills.as_context(),
        )

    def matching_skill(self, user_input: str):
        return self.skills.match(user_input)

    def respond(self, user_input: str) -> str:
        """Ask Claude for a reply, grounded in the accumulated memory and skills."""
        skill = self.matching_skill(user_input)
        if skill:
            self.skills.mark_used(skill["name"])

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=self.build_system_prompt(),
            messages=[{"role": "user", "content": user_input}],
        )
        return "".join(block.text for block in message.content if block.type == "text")

    def remember(self, fact: str, tags: Optional[List[str]] = None):
        return self.memory.remember(fact, tags)

    def learn_skill(
        self,
        name: str,
        description: str,
        steps: List[str],
        triggers: Optional[List[str]] = None,
    ):
        return self.skills.save_skill(name, description, steps, triggers)

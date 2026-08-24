"""Interactive REPL for the Hermes agent.

Usage:
    ANTHROPIC_API_KEY=... python -m hermes.cli
"""
from __future__ import annotations

from .agent import HermesAgent

HELP_TEXT = """\
명령어:
  /remember <내용>          기억에 사실을 하나 저장합니다.
  /memory                   지금까지 저장된 기억을 봅니다.
  /skill save <이름> | <설명> | <단계1;단계2;...> | <트리거1,트리거2>
                             새 스킬을 저장합니다 (뒤 두 항목은 생략 가능).
  /skills                   저장된 스킬 목록을 봅니다.
  /help                     이 도움말을 봅니다.
  /exit                     종료합니다.

명령어 없이 입력하면 Claude에게 질문합니다. 같은 유형의 요청을 반복하면
Hermes가 스킬로 저장할지 먼저 알려줍니다.
"""


def _handle_skill_save(agent: HermesAgent, payload: str) -> None:
    parts = [p.strip() for p in payload.split("|")]
    name = parts[0] if len(parts) > 0 else ""
    description = parts[1] if len(parts) > 1 else ""
    steps = [s.strip() for s in parts[2].split(";") if s.strip()] if len(parts) > 2 else []
    triggers = [t.strip() for t in parts[3].split(",") if t.strip()] if len(parts) > 3 else []
    if not name:
        print("사용법: /skill save <이름> | <설명> | <단계1;단계2> | <트리거1,트리거2>")
        return
    agent.learn_skill(name, description, steps, triggers)
    print(f"[스킬 저장됨] {name}")


def run() -> None:
    agent = HermesAgent()
    print("Hermes Agent 시작. /help 로 명령어를 확인하세요.\n")
    while True:
        try:
            user_input = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n종료합니다.")
            break

        if not user_input:
            continue
        if user_input in ("/exit", "/quit"):
            print("종료합니다.")
            break
        if user_input == "/help":
            print(HELP_TEXT)
            continue
        if user_input.startswith("/remember "):
            fact = user_input[len("/remember "):].strip()
            agent.remember(fact)
            print(f"[기억함] {fact}")
            continue
        if user_input == "/memory":
            print(agent.memory.as_context())
            continue
        if user_input == "/skills":
            print(agent.skills.as_context())
            continue
        if user_input.startswith("/skill save "):
            _handle_skill_save(agent, user_input[len("/skill save "):])
            continue

        count = agent.observe_task(user_input)
        if count >= agent.SKILL_LEARN_THRESHOLD:
            print(
                f"[Hermes] 비슷한 요청을 {count}번째 하고 계시네요. "
                "'/skill save <이름> | <설명> | <단계1;단계2>' 로 저장해두면 "
                "다음부터 더 빨리 처리할 수 있어요."
            )

        skill = agent.matching_skill(user_input)
        if skill:
            print(f"[Hermes] 저장된 스킬 '{skill['name']}' 을 적용합니다: {skill['description']}")
            for i, step in enumerate(skill.get("steps", []), 1):
                print(f"  {i}. {step}")

        try:
            reply = agent.respond(user_input)
        except Exception as exc:  # network issues / missing credentials
            reply = f"(Claude 응답 실패: {exc}. ANTHROPIC_API_KEY 환경변수를 설정했는지 확인하세요.)"
        print(f"hermes> {reply}\n")


if __name__ == "__main__":
    run()

# Hermes Agent

쓸수록 사용자를 더 잘 기억하고, 반복되는 작업을 스스로 "스킬"로 저장해
다음번에는 더 빠르게 처리하는 독립형 AI 에이전트 프레임워크입니다.
(canco-app 저장소와는 별개의 프로젝트로, `hermes-agent/` 디렉토리 아래에
존재합니다.)

## 핵심 개념

- **영구 기억 (`hermes/memory.py`)** — 대화에서 알게 된 사실을 JSON 파일에
  누적 저장합니다. 세션이 끝나도 사라지지 않고, 다음 실행 때 시스템
  프롬프트에 포함되어 Claude에게 전달됩니다.
- **스킬화 (`hermes/skills.py`)** — 같은 유형의 요청이 반복되면
  (`HermesAgent.SKILL_LEARN_THRESHOLD`, 기본 2회) 에이전트가 이를
  감지해서 스킬로 저장하라고 제안합니다. 저장된 스킬은 이름·설명·단계·
  트리거 키워드를 가지며, 이후 트리거와 일치하는 요청이 오면 바로
  인식되어 재사용됩니다.
- **에이전트 루프 (`hermes/agent.py`)** — 위 두 저장소를 시스템 프롬프트로
  엮어 Anthropic Claude API를 호출합니다.

## 설치

```bash
cd hermes-agent
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
```

## 실행 (대화형 REPL)

```bash
python -m hermes.cli
```

```
you> /remember 사용자는 매주 금요일에 릴리즈 빌드를 만든다
[기억함] 사용자는 매주 금요일에 릴리즈 빌드를 만든다

you> 릴리즈 빌드 준비해줘
you> 릴리즈 빌드 준비해줘
[Hermes] 비슷한 요청을 2번째 하고 계시네요. '/skill save <이름> | <설명> | <단계1;단계2>' 로 저장해두면 다음부터 더 빨리 처리할 수 있어요.

you> /skill save release_build | Android 릴리즈 빌드 생성 | gradlew assembleRelease 실행;apk 서명 확인 | 릴리즈 빌드,release build
[스킬 저장됨] release_build

you> 릴리즈 빌드 준비해줘
[Hermes] 저장된 스킬 'release_build' 을 적용합니다: Android 릴리즈 빌드 생성
  1. gradlew assembleRelease 실행
  2. apk 서명 확인
hermes> ...
```

## REPL 명령어

| 명령어 | 설명 |
| --- | --- |
| `/remember <내용>` | 사실을 영구 기억에 저장 |
| `/memory` | 저장된 기억 목록 보기 |
| `/skill save <이름> \| <설명> \| <단계1;단계2> \| <트리거1,트리거2>` | 스킬 저장 |
| `/skills` | 저장된 스킬 목록 보기 |
| `/help` | 도움말 |
| `/exit` | 종료 |

## 코드로 직접 사용하기

```python
from hermes import HermesAgent

agent = HermesAgent()
agent.remember("사용자는 Kotlin과 Gradle을 주로 쓴다")
agent.learn_skill(
    name="release_build",
    description="Android 릴리즈 빌드 생성",
    steps=["gradlew assembleRelease 실행", "apk 서명 확인"],
    triggers=["릴리즈 빌드", "release build"],
)

count = agent.observe_task("릴리즈 빌드 해줘")  # 반복 횟수 추적
skill = agent.matching_skill("릴리즈 빌드 해줘")  # 매칭되는 스킬 조회
reply = agent.respond("릴리즈 빌드 해줘")          # Claude 호출 (ANTHROPIC_API_KEY 필요)
```

## 테스트

API 키 없이 메모리/스킬 로직만 검증합니다.

```bash
cd hermes-agent
pip install pytest
pytest
```

## 저장 위치

- `memory/memory.json` — 영구 기억 (기본 경로, git에는 커밋되지 않음)
- `skills/skills.json` — 스킬 라이브러리 (기본 경로, git에는 커밋되지 않음)

두 파일 모두 `Memory(path=...)` / `SkillLibrary(path=...)` 로 위치를
바꿀 수 있습니다.

## 현재 범위와 한계

- MVP 단계로, 스킬 매칭은 트리거 키워드 포함 여부로 판단하는 단순한
  방식입니다 (임베딩 기반 유사도 매칭은 다음 단계).
- 스킬의 "단계"는 사람이 직접 정의해 저장하며, 에이전트가 자동으로
  실행 결과를 검증하지는 않습니다 (실제 셸/파일 조작 도구 연동은 아직
  없음 — 안전하게 범위를 좁혀 시작했습니다).
- `respond()`는 Anthropic API 호출이 필요하므로 `ANTHROPIC_API_KEY`가
  없으면 대화 기능은 동작하지 않고, 기억/스킬 저장·조회 기능만
  사용할 수 있습니다.

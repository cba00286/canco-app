# Hermes Agent — 로컬 설치 가이드

"Hermes Agent"는 이 저장소에서 새로 만든 프레임워크가 아니라,
**Nous Research가 만든 실제 오픈소스 프로젝트**입니다 (MIT 라이선스).
쓸수록 사용자를 기억하고, 반복되는 작업을 절차 기억(procedural memory)으로
"스킬"화해서 다음번에는 더 빠르게 처리하는 자율 에이전트입니다.

- 공식 사이트: https://hermes-agent.nousresearch.com
- 공식 문서: https://hermes-agent.nousresearch.com/docs/
- 소스코드: https://github.com/NousResearch/hermes-agent

이 폴더(`hermes-agent/`)는 그 실제 프로젝트를 **여러분의 로컬 머신**에
설치하고 구성하기 위한 가이드와 스크립트만 담고 있습니다. canco-app
저장소(Android 앱 빌드 자동화) 자체에는 Hermes Agent 구동에 필요한 요소가
없으므로, 아래 절차는 클라우드 샌드박스가 아니라 직접 소유한 로컬
컴퓨터에서 실행하세요.

## 왜 로컬에서 실행해야 하나요?

- **상시 실행 전제**: cron 작업, 메신저 게이트웨이(Telegram/Discord/Slack
  등)를 갖춘 도구라, 일회성으로 사라지는 클라우드 컨테이너에는 맞지
  않습니다.
- **강력한 도구 접근 권한**: 파일시스템·셸 접근이 가능한 자율 에이전트이므로
  신뢰할 수 있는 본인 소유 환경에서 실행해야 안전합니다. (참고: 이 종류의
  자율 에이전트가 "무인(YOLO) 모드"로 악용된 보안 사고 사례가 실제로
  보고된 바 있으니, 초기 설정 시 어떤 도구에 어떤 권한을 줄지 신중히
  검토하세요.)

## 설치

### Linux / macOS / WSL2 / Termux

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
source ~/.bashrc
hermes
```

### Windows (PowerShell)

```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

설치 스크립트가 `uv`, Python 3.11, Node.js, ripgrep, ffmpeg를 자동으로
준비합니다.

또는 이 저장소에 포함된 [`setup-local.sh`](./setup-local.sh)를 로컬
머신에서 실행해도 됩니다 (아래 참고).

## 완전히 로컬 모델로만 실행하기 (Ollama, API 키 불필요)

클라우드 API 키/구독 없이 완전히 로컬에서 돌리려면 Ollama를 함께
사용하세요.

```bash
# 1) Ollama 설치(https://ollama.com) 후 원하는 모델 받기
ollama pull llama3.1

# 2) Ollama 실행 (OpenAI 호환 API를 127.0.0.1:11434 에 노출)
ollama serve

# 3) Hermes Agent가 Ollama를 바라보도록 설정
hermes config set model.provider custom
hermes config set model.base_url http://127.0.0.1:11434/v1
hermes config set model.name llama3.1
```

대화형으로 설정하려면 `hermes model`을 실행해 커스텀 엔드포인트를
선택해도 됩니다.

## 기본 사용법

```bash
hermes                 # 대화형 CLI 시작
hermes model           # LLM 제공자/모델 선택
hermes tools           # 사용할 도구 구성
hermes gateway setup   # 메신저(Telegram/Discord 등) 연동 (선택)
hermes doctor          # 설치/설정 문제 진단
hermes update          # 최신 버전으로 업데이트
```

CLI 안에서 자주 쓰는 슬래시 명령어:

| 명령어 | 설명 |
| --- | --- |
| `/skills` | 지금까지 학습된 스킬 목록 확인 |
| `/model [name]` | 모델 즉시 전환 |
| `/new`, `/reset` | 새 대화 시작 |
| `/compress`, `/usage` | 컨텍스트 최적화 및 사용량 확인 |

## 참고

이 README는 공식 문서(위 링크)를 바탕으로 정리한 로컬 설치 요약입니다.
최신 정보는 항상 공식 문서를 우선하세요.

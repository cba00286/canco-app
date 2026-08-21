# 「쿵쿵이와 친구들」 1화 — AI 영상 제작 파이프라인

원본 인수인계 문서(`docs/00_원본_인수인계.md`)의 4단계 작업(캐릭터 레퍼런스 → 씬 키프레임 →
이미지→영상 클립 → 편집)을 실행 가능한 파이프라인으로 구현한 것이다.

---

## ⚠️ 먼저 읽을 것 — 이 저장소 세션에서 생성이 실행되지 못한 이유

이 세션의 실행 환경은 아웃바운드 HTTPS가 조직 정책 프록시를 거치는데, **`huggingface.co`와
`*.hf.space`가 정책상 차단(403)** 되어 있다. Hugging Face MCP 커넥터도 `gradio=none` 설정으로
`invoke`가 비활성화되어 있어, 실제 이미지·영상 생성은 이 환경에서 수행할 수 없었다.

```
connect_rejected: gateway answered 403 to CONNECT — huggingface.co:443
connect_rejected: gateway answered 403 to CONNECT — mcp-tools-qwen-image-fast.hf.space:443
```

그래서 **HF 접속이 가능한 환경(본인 PC 등)에서 그대로 돌리면 되는 파이프라인**을 완성해 두었다.
프롬프트 조립·파라미터 방어 로직·편집(ffmpeg) 단계는 이 환경에서 실제로 검증했고,
Space API 스키마도 MCP `view_parameters`로 실물 확인해 반영했다(아래 표).

| 항목 | 상태 |
|---|---|
| 캐릭터/씬 프롬프트 데이터화 + 자리표시자 치환 | ✅ 검증 완료(dry-run) |
| Space API 스키마 확인 및 반영 | ✅ 실물 확인 (Qwen-Image-Fast / Qwen-Image / wan2-2 / Qwen-Image-Edit LoRA) |
| ffmpeg 이어붙이기 + 배경음악 합성 | ✅ 더미 클립 8개로 실제 실행 검증 |
| 실제 이미지·영상 생성 | ⛔ 이 환경에서 HF 차단 — 사용자 환경에서 실행 필요 |

---

## 실행 방법

```bash
pip install -r requirements.txt
export HF_TOKEN=hf_xxxxxxxx          # ZeroGPU 쿼터는 계정 단위라 로그인 권장

cd kungkung-ep1
python3 scripts/pipeline.py chars      # 1) 캐릭터 레퍼런스 6종
python3 scripts/pipeline.py scenes     # 2) 씬 키프레임 9종
python3 scripts/pipeline.py videos     # 3) 키프레임 → 4~5초 클립
python3 scripts/pipeline.py assemble   # 4) 이어붙이기 + 테마곡 합성

python3 scripts/pipeline.py all        # 1~4 한 번에
```

유용한 옵션:

| 옵션 | 설명 |
|---|---|
| `--dry-run` | 네트워크 호출 없이 최종 프롬프트만 출력 (프롬프트 수정 시 먼저 확인용) |
| `--only S5 S6` | 특정 씬·캐릭터만 실행 (`--only 쿵쿵 루카`) |
| `--force` | 이미 생성된 결과물도 다시 생성 (톤이 안 맞는 컷 재뽑기) |
| `--image-space mcp-tools/Qwen-Image` | 고품질 Space로 교체 (기본은 Fast) |
| `--steps 8` / `--video-steps 6` | 추론 스텝 수 |
| `--theme path/to/theme.mp3` | 배경음악 경로 지정 (기본 `assets/theme_song.mp3`) |

생성 결과는 `outputs/`에 저장되고, 어떤 Space·seed·프롬프트로 만들었는지는
`outputs/manifest.json`에 기록되어 그대로 재현할 수 있다.
(미디어 파일 자체는 `.gitignore`로 저장소에 올리지 않는다.)

---

## 구조

```
kungkung-ep1/
├── prompts/characters.json   # 캐릭터 6종 고정 묘사 + seed
├── prompts/scenes.json       # 씬 9종 이미지/모션 프롬프트
├── scripts/pipeline.py       # 4단계 실행기
├── reference/                # 쿵쿵이 공식 레퍼런스 이미지
├── docs/00_원본_인수인계.md   # 원본 기획 문서
└── outputs/                  # characters / scenes / videos / manifest.json
```

### 프롬프트 자리표시자

`scenes.json` 안의 `{루카}`는 **전체 묘사**, `[루카]`는 **축약 묘사**로 치환된다.
등장인물이 6명인 엔딩 컷에 전체 묘사를 6번 넣으면 프롬프트가 250단어를 넘어 연출 지시가
희석되므로, **주인공 쿵쿵과 그 컷의 주연만 전체 묘사, 나머지는 축약 묘사**를 쓴다.
현재 전 씬이 200단어 이하로 맞춰져 있다(S1 107 / S7 198 / ENDING 187).

### 쿵쿵이 묘사 보정

사용자가 제공한 공식 레퍼런스 이미지(`reference/kungkung_official_reference.png`)에 맞춰
원본 문서의 묘사를 수정했다.

| 항목 | 원본 문서 | 보정본 (레퍼런스 기준) |
|---|---|---|
| 피부 | pastel green | soft pastel **mint**-green + **cream 배색 배·주둥이** |
| 눈 | brown eyes | **green-hazel** eyes with bright catchlights |
| 목 | floral ivory scarf | ivory **bandana** with colorful **tropical** floral pattern |
| 추가 | — | 낮고 둥근 스캘럽 형태의 **beige neck frill** |

---

## 확인된 Space API 스키마 (MCP `view_parameters` 실물 확인)

원본 문서의 경고대로 파라미터명이 Space마다 다르다. 실제 확인 결과는 아래와 같고,
`pipeline.py`는 여기에 더해 **호출 직전 `view_api()`로 엔드포인트와 파라미터를 읽어
존재하지 않는 인자는 자동으로 빼고 보낸다.** Space가 업데이트돼도 죽지 않는다.

**이미지 — `mcp-tools/Qwen-Image-Fast`** (엔드포인트: `generate_image`)
`prompt`, `aspect_ratio`(기본 `16:9`), `num_inference_steps`(기본 8), `guidance_scale`(기본 1),
`seed`, `randomize_seed`(기본 true) → `(PIL Image, seed)` 반환. **`negative_prompt` 없음.**

**이미지(고품질) — `mcp-tools/Qwen-Image`** (엔드포인트: `generate_image`)
위와 동일 + **`negative_prompt` 있음**, `guidance_scale` 기본 4, `num_inference_steps` 기본 16
(16 이하로 둬야 30초 안에 끝난다).

**영상 — `zerogpu-aoti/wan2-2-fp8da-aoti-faster`** (엔드포인트: `generate_video`)
`input_image`(**공개 URL 또는 gradio 업로드 파일**), `prompt`, `negative_prompt`,
`duration_seconds`(기본 3.5), `steps`(기본 6), `guidance_scale`/`guidance_scale_2`, `seed`,
`randomize_seed` → `(mp4 경로, seed)` 반환. 프레임 수 = `duration_seconds × 24fps`,
출력 해상도는 32의 배수로 보정된다.

**이미지 편집(일관성용) — `prithivMLmods/Qwen-Image-Edit-2509-LoRAs-Fast`**
`image_b64`(**파일이 아니라 base64 문자열**), `prompt`, `lora_adapter`, `steps`,
`guidance_scale`, `seed`, `randomize_seed` → `{"image": base64 PNG data URL, "seed": ...}`.

> `mcp-tools/wan-2-2-first-last-frame`, `mcp-tools/Qwen-Image-Edit-Angles`는 확인 시점에
> 503(Space 휴면) 상태여서 스키마를 못 받았다. 쓰려면 깨운 뒤 `view_parameters`로 재확인할 것.

---

## 남은 작업

1. **실제 생성 실행** — HF 접속이 되는 환경에서 `python3 scripts/pipeline.py all`.
   ZeroGPU 무료 계정은 대기열·쿼터 제한이 있어 단계별로 나눠 돌리는 편이 안전하다
   (스크립트에 4회 지수 백오프 재시도가 들어 있다).
2. **캐릭터 일관성 선별** — 프롬프트만으로는 완벽히 고정되지 않는다. `--force`로 여러 번
   뽑은 뒤 톤이 가장 맞는 컷을 남기고, 필요하면 `Qwen-Image-Edit` 계열로 레퍼런스 기반
   각도 변형을 쓰는 편이 낫다(위 base64 입력 형식 주의).
3. **S#7은 초안** — 원본 인수인계 문서에 S#6 다음이 바로 S#8이라 7번 씬이 비어 있었다.
   S#6(첫걸음·이름 받기) → S#8(개울가에서 소미를 구함) 사이를 잇도록
   「서툰 첫 나들이」(쿵쿵이 뿌리에 걸려 넘어지고 친구들이 일으켜 세우는 컷)를 새로 써 넣었다.
   `scenes.json`에서 `"draft": true`로 표시해 두었으니, 확정 대본이 나오면 그 항목의
   `title`/`image`/`motion`만 갈아끼우면 된다.
4. **테마곡** — Suno는 API가 유료 플랜이라 자동화 대상에서 뺐다. 웹/앱에서 생성해
   `assets/theme_song.mp3`로 두면 `assemble` 단계가 자동으로 합성한다.
5. **클립 길이** — 클립이 4~5초라 실제 연출 길이와 맞추려면 반복재생·속도조절 편집이 필요하다.

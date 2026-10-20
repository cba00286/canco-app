# Postiz 셀프호스팅 (무료, 오픈소스)

SNS 예약 발행 서버. NAS 또는 100.100.100.199 서버에 Docker로 올린다. 모든 설정은 `.env`.

## 배포
1. `cp .env.example .env` → `POSTIZ_URL`, `DB_PASSWORD`, `JWT_SECRET`(`openssl rand -hex 32`), `DATA_DIR`, `BACKUP_DIR` 입력
2. `./scripts/deploy.sh`
3. 브라우저에서 `POSTIZ_URL` 접속 → 관리자 계정 생성 → `.env`의 `DISABLE_REGISTRATION=true` 후 `docker compose up -d`
4. SNS 연결용 API 키는 `.env.providers`에 추가 (각 SNS 개발자 앱 필요, 대부분 무료)
5. CLI: `export POSTIZ_API_URL=<POSTIZ_URL>/api`, `export POSTIZ_API_KEY=<설정 화면에서 발급>`

## 백업 / 복구
- `./scripts/backup.sh` : DB + 업로드 + 설정 + .env 백업 (`BACKUP_KEEP`개 유지). cron/작업 스케줄러 등록 권장
- `./scripts/restore.sh backups/<타임스탬프>` : 복구 전에 현재 상태를 자동 백업하므로 되돌리기 가능
- 업데이트(`deploy.sh`)도 실행 전에 자동 백업

## 주의
- 한국 서비스(네이버 블로그, 카카오 등)는 Postiz 기본 지원 목록에 없을 수 있다. 연결 전 지원 SNS 목록 확인.
- 최신 Postiz 버전은 필요 컴포넌트가 바뀔 수 있으니 배포 전 공식 compose와 대조.
- NAS 업로드 원칙: `DATA_DIR`/`BACKUP_DIR`는 NAS(100.100.100.220) 볼륨을 가리키게 한다.

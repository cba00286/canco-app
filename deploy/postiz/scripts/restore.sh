#!/usr/bin/env bash
# 사용: scripts/restore.sh <백업폴더>   (복구 직전 현재 상태를 자동으로 한 번 더 백업한다)
set -euo pipefail
cd "$(dirname "$0")/.."
SRC="${1:?사용법: restore.sh <backups/타임스탬프 폴더>}"
[ -f "$SRC/db.dump" ] && [ -f "$SRC/files.tar.gz" ] || { echo "백업 폴더가 올바르지 않음: $SRC"; exit 1; }
set -a; . ./.env; set +a
echo "[1/4] 복구 전 현재 상태 안전 백업"; ./scripts/backup.sh
echo "[2/4] 앱 중지"; docker compose stop postiz
echo "[3/4] DB 복구"
docker exec -i "${COMPOSE_PROJECT_NAME}-postgres" pg_restore -U "$DB_USER" -d "$DB_NAME" --clean --if-exists < "$SRC/db.dump"
echo "[4/4] 파일 복구 후 앱 시작"
tar -xzf "$SRC/files.tar.gz" -C "$DATA_DIR"
docker compose start postiz
echo "restore ok: $SRC"

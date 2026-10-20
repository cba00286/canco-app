#!/usr/bin/env bash
# DB 덤프 + 업로드/설정 아카이브를 타임스탬프로 저장하고 오래된 것을 정리한다.
set -euo pipefail
cd "$(dirname "$0")/.."
set -a; . ./.env; set +a
TS=$(date +%Y%m%d-%H%M%S)
DEST="${BACKUP_DIR}/${TS}"
mkdir -p "$DEST"
docker exec "${COMPOSE_PROJECT_NAME}-postgres" pg_dump -U "$DB_USER" -d "$DB_NAME" -Fc > "$DEST/db.dump"
tar -czf "$DEST/files.tar.gz" -C "$DATA_DIR" uploads config
cp .env "$DEST/env.backup" && chmod 600 "$DEST/env.backup"
echo "backup ok: $DEST"
# 보관 개수 초과분 삭제 (BACKUP_DIR 하위 타임스탬프 폴더만)
ls -1d "${BACKUP_DIR}"/[0-9]*-[0-9]* 2>/dev/null | sort | head -n -"${BACKUP_KEEP}" | xargs -r rm -rf

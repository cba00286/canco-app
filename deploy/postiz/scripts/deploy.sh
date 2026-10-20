#!/usr/bin/env bash
# 최초 배포/업데이트. 업데이트 전에 항상 백업한다.
set -euo pipefail
cd "$(dirname "$0")/.."
[ -f .env ] || { echo ".env 가 없음: cp .env.example .env 후 값 입력"; exit 1; }
[ -f .env.providers ] || touch .env.providers
set -a; . ./.env; set +a
: "${POSTIZ_URL:?POSTIZ_URL 필요}" "${DB_PASSWORD:?DB_PASSWORD 필요}" "${JWT_SECRET:?JWT_SECRET 필요}"
mkdir -p "$DATA_DIR"/{config,uploads,postgres,redis} "$BACKUP_DIR"
if docker ps -a --format '{{.Names}}' | grep -q "^${COMPOSE_PROJECT_NAME}-postgres$"; then ./scripts/backup.sh; fi
docker compose pull
docker compose up -d
docker compose ps

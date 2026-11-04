#!/bin/sh
# Sao luu database hang ngay. Chay tu thu muc goc cua repo:
#     sh infra/backup/backup-db.sh
# Dat lich (Linux, 2h sang moi ngay):
#     0 2 * * * cd /duong/dan/repo && sh infra/backup/backup-db.sh
# Khoi phuc mot ban:
#     docker compose -f infra/docker-compose.yml exec -T db \
#         pg_restore -U labuser -d labdb --clean --if-exists < infra/backup/files/<file>.dump
set -eu

KEEP_DAYS="${KEEP_DAYS:-30}"
OUT_DIR="$(dirname "$0")/files"
mkdir -p "$OUT_DIR"

FILE="$OUT_DIR/labdb-$(date +%Y%m%d-%H%M%S).dump"
docker compose -f infra/docker-compose.yml exec -T db \
    sh -c 'pg_dump -U "$POSTGRES_USER" -Fc "$POSTGRES_DB"' > "$FILE"
echo "Da sao luu: $FILE ($(du -h "$FILE" | cut -f1))"

# Xoa ban cu hon KEEP_DAYS ngay
find "$OUT_DIR" -name 'labdb-*.dump' -mtime +"$KEEP_DAYS" -delete

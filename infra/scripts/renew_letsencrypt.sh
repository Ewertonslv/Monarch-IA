#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ENV_FILE:-${ROOT_DIR}/infra/deploy/.env}"

cd "$ROOT_DIR"

docker compose --env-file "$ENV_FILE" run --rm certbot renew --webroot --webroot-path /var/www/certbot
docker compose --env-file "$ENV_FILE" restart nginx

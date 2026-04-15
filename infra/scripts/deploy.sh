#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ENV_FILE:-${ROOT_DIR}/infra/deploy/.env}"

cd "$ROOT_DIR"

if [ ! -f "$ENV_FILE" ]; then
  echo "Arquivo de ambiente do deploy não encontrado: $ENV_FILE" >&2
  exit 1
fi

echo "Atualizando repositório"
git pull --ff-only

echo "Subindo containers"
docker compose --env-file "$ENV_FILE" up -d --build --remove-orphans

echo "Deploy concluído"

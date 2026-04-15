#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ENV_FILE:-${ROOT_DIR}/deploy/.env}"

if [ ! -f "$ENV_FILE" ]; then
  echo "Arquivo de ambiente do deploy não encontrado: $ENV_FILE" >&2
  exit 1
fi

set -a
source "$ENV_FILE"
set +a

: "${DOMAIN:?DOMAIN is required}"
: "${LETSENCRYPT_EMAIL:?LETSENCRYPT_EMAIL is required}"

cd "$ROOT_DIR"

echo "Subindo stack em modo HTTP para validação ACME"
docker compose --env-file "$ENV_FILE" up -d monarch-ai whatsapp-bot nginx

echo "Solicitando certificado para ${DOMAIN}"
docker compose --env-file "$ENV_FILE" run --rm certbot certonly \
  --webroot \
  --webroot-path /var/www/certbot \
  --email "$LETSENCRYPT_EMAIL" \
  --agree-tos \
  --no-eff-email \
  -d "$DOMAIN"

echo "Reiniciando nginx para carregar HTTPS"
docker compose --env-file "$ENV_FILE" restart nginx

echo "Certificado emitido com sucesso"

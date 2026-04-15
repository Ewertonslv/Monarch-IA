#!/bin/sh
set -eu

DOMAIN="${DOMAIN:?DOMAIN environment variable is required}"
CERT_PATH="/etc/letsencrypt/live/${DOMAIN}/fullchain.pem"

if [ -f "$CERT_PATH" ]; then
  TEMPLATE="/etc/nginx/templates/https.conf.template"
  echo "Using HTTPS nginx template for ${DOMAIN}"
else
  TEMPLATE="/etc/nginx/templates/http.conf.template"
  echo "Using HTTP-only nginx template for ${DOMAIN}"
fi

sed "s|\${DOMAIN}|${DOMAIN}|g" "$TEMPLATE" > /etc/nginx/conf.d/default.conf
exec nginx -g 'daemon off;'

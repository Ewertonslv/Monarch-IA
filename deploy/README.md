# Deploy no Hetzner Cloud

> Pasta legada temporaria. O caminho canonico agora e `infra/deploy/`.

Esta pasta deixa pronta a infraestrutura para subir o ecossistema inicial com Docker, Nginx e Let's Encrypt assim que o servidor estiver liberado.

## Arquivos principais

- `docker-compose.yml`: sobe PostgreSQL, Monarch AI, Monarch Core, WhatsApp Bot, Nginx e Certbot
- `Dockerfile`: imagem do Monarch AI
- `monarch_phase1/core_api/Dockerfile`: imagem do Monarch Core
- `apps/monarch-core/Dockerfile`: imagem do Monarch Core
- `apps/whatsapp-notion-bot/Dockerfile`: imagem do WhatsApp Bot
- `deploy/nginx/templates/*.template`: roteamento HTTP/HTTPS
- `scripts/bootstrap_ubuntu_2404.sh`: instala Docker e Compose no Ubuntu 24.04
- `scripts/deploy.sh`: faz `git pull` e `docker compose up -d --build`
- `scripts/init_letsencrypt.sh`: emite o primeiro certificado
- `scripts/renew_letsencrypt.sh`: renova certificado depois

## Roteamento

- `https://SEU_DOMINIO/` -> Monarch AI
- `https://SEU_DOMINIO/api/` -> Monarch Core
- `https://SEU_DOMINIO/webhook` -> WhatsApp Notion Bot
- `https://SEU_DOMINIO/core-health` -> healthcheck do Monarch Core
- `https://SEU_DOMINIO/bot-health` -> healthcheck do bot

## Arquivos de ambiente

Copie estes arquivos antes do primeiro deploy:

```bash
cp deploy/.env.example deploy/.env
cp deploy/env/monarch.env.example deploy/env/monarch.env
cp deploy/env/monarch-core.env.example deploy/env/monarch-core.env
cp deploy/env/whatsapp.env.example deploy/env/whatsapp.env
```

Preencha:

- `deploy/.env`
  - `DOMAIN`
  - `LETSENCRYPT_EMAIL`
  - `MONARCH_DB_PASSWORD`
- `deploy/env/monarch.env`
  - credenciais do Monarch AI
- `deploy/env/monarch-core.env`
  - configuracao do Monarch Core
  - `MONARCH_CORE_API_KEY` (recomendado em producao)
- `deploy/env/whatsapp.env`
  - credenciais do WhatsApp Bot

## Seguranca e rate limit

- Nginx com rate limit por IP:
  - `/webhook`: 30 req/min
  - `/api/*`: 120 req/min
  - `/` (hub/runtime): 300 req/min
- Fallback de rate limit nos apps:
  - Monarch Core (`/api/*`)
  - Monarch Web (`/hub/*` e `/tasks*`)
  - WhatsApp Bot (`/webhook`)
- Headers de seguranca aplicados em app e proxy:
  - `X-Frame-Options: DENY`
  - `X-Content-Type-Options: nosniff`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Permissions-Policy` restritivo
- Header interno opcional para Core API:
  - Quando `MONARCH_CORE_API_KEY` estiver definido no core, chamadas para `/api/*` devem enviar `X-API-Key` correspondente.

## Ordem recomendada quando o servidor estiver pronto

1. Apontar o DNS do domínio para o IP público do servidor.
2. Subir o código para o servidor.
3. Rodar `scripts/bootstrap_ubuntu_2404.sh`.
4. Preencher os arquivos `deploy/.env`, `deploy/env/monarch.env`, `deploy/env/monarch-core.env` e `deploy/env/whatsapp.env`.
5. Rodar `scripts/deploy.sh`.
6. Rodar `scripts/init_letsencrypt.sh`.
7. Configurar a Z-API para usar `https://SEU_DOMINIO/webhook`.

## Observações

- O SQLite do Monarch AI fica persistido no volume Docker `monarch_data`.
- O PostgreSQL do Monarch Core fica persistido no volume Docker `monarch_postgres_data`.
- Antes de emitir o certificado, o Nginx sobe em HTTP simples automaticamente.
- Depois que o certificado existe, o Nginx troca sozinho para HTTPS ao reiniciar.

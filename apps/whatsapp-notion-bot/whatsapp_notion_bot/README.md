# WhatsApp Notion Bot

Aplicacao em Python que recebe mensagens do WhatsApp via webhook da Z-API, usa Claude para classificar gastos pessoais e registra cada despesa em uma base do Notion.

## Requisitos

- Python 3.11+
- Credenciais de:
  - Anthropic
  - Z-API
  - Notion

## Estrutura

```text
apps/
  whatsapp-notion-bot/
    Dockerfile
    whatsapp_notion_bot/
      main.py
      classifier.py
      notion_client.py
      zapi_client.py
      config.py
      tests/
        test_classifier.py
        test_notion_client.py
        test_zapi_client.py
```

## Configuracao

1. Crie um arquivo `.env` na raiz do projeto com base em `apps/whatsapp-notion-bot/whatsapp_notion_bot/.env.example`.
2. Preencha as variaveis:

```env
ANTHROPIC_API_KEY=
ZAPI_INSTANCE_ID=
ZAPI_TOKEN=
ZAPI_CLIENT_TOKEN=
NOTION_TOKEN=
NOTION_DATABASE_ID=
MY_PHONE_NUMBER=
```

## Instalacao

```bash
pip install -e .[dev]
```

Se voce quiser rodar este bot isoladamente com Python 3.11+, sem depender do `pyproject.toml` raiz do repositorio:

```bash
pip install -r apps/whatsapp-notion-bot/whatsapp_notion_bot/requirements.txt
pip install pytest pytest-asyncio
```

## Executando

```bash
uvicorn whatsapp_notion_bot.main:app --reload
```

Webhook:

- `POST /webhook`
- Aceita apenas mensagens vindas de `MY_PHONE_NUMBER`

Mensagem de exemplo:

```text
Gastei R$45 no almoco
```

Resposta esperada no WhatsApp:

```text
\u2705 R$45.00 em Alimentacao - registrado
```

## Como funciona

1. O webhook recebe o payload da Z-API.
2. O numero do remetente e o texto da mensagem sao extraidos.
3. Claude (`claude-haiku-4-5-20251001`) classifica e retorna `amount`, `category`, `description` e `date`.
4. A despesa e criada no banco do Notion.
5. Uma confirmacao e enviada ao usuario pelo WhatsApp.

## Testes

Os testes nao fazem chamadas reais para APIs externas.

```bash
pytest apps/whatsapp-notion-bot/whatsapp_notion_bot/tests
```

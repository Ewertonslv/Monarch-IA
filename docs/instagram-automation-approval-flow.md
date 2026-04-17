# Instagram Automation Approval Flow

Data: 2026-04-16
Objetivo: detalhar o fluxo tecnico de operacao assistida do projeto `Instagram Automation`.

## Visao geral

Esse projeto nao deve ser tratado como publicacao 100% automatica.

O fluxo principal desejado e:

1. gerar proposta de conteudo
2. montar legenda e CTA
3. enviar proposta para revisao no Telegram
4. permitir `aprovar`, `pedir ajuste` ou `rejeitar`
5. reenviar proposta ajustada
6. publicar somente depois do ok final

## Estado atual da base

A base do app em `apps/instagram-automation` agora ja suporta:

- fila de conteudo
- status de aprovacao
- status de `needs_revision`
- historico de feedback
- reenfileiramento para nova aprovacao

## Estados recomendados

- `awaiting_approval`
- `needs_revision`
- `approved`
- `published`
- `rejected`

## Estrutura minima de cada proposta

Cada item da fila deve carregar pelo menos:

- titulo
- hook
- formato
- pilar
- objetivo
- audiencia
- estrutura de legenda
- CTA
- hashtags
- canal de aprovacao
- quantidade de revisoes
- historico de feedback

## Fluxo tecnico recomendado

### Etapa 1. Geracao

Entrada:
- nicho
- objetivo
- audiencia
- pilares
- CTA

Saida:
- proposta de conteudo
- legenda base
- hashtags
- item salvo na fila com status `awaiting_approval`

### Etapa 2. Envio para Telegram

O app deve enviar para o Telegram:

- titulo do conteudo
- hook
- formato
- resumo da legenda
- CTA
- botoes de acao

Botoes esperados:
- `aprovar`
- `pedir ajuste`
- `rejeitar`

### Etapa 3. Pedido de ajuste

Se o usuario pedir ajuste:

- o item vai para `needs_revision`
- o feedback entra em `feedback_history`
- o contador de revisoes sobe
- o conteudo volta para o fluxo de ajuste

### Etapa 4. Reenvio

Depois do ajuste:

- o item volta para `awaiting_approval`
- opcionalmente registra observacao do que foi mudado
- e reenviado ao Telegram

### Etapa 5. Aprovacao final

Quando aprovado:

- status vira `approved`
- o app pode seguir para publicacao ou agendamento

### Etapa 6. Publicacao

Depois da postagem:

- status vira `published`
- o app deve registrar dados minimos de publicacao

## Integracao futura com Telegram

Quando as credenciais estiverem prontas, a implementacao deve seguir esta ideia:

1. gerar conteudo localmente
2. montar payload legivel para Telegram
3. enviar mensagem com acoes
4. receber decisao
5. atualizar fila local

## MVP tecnico recomendado

### Fase 1

- fila local
- aprovar
- rejeitar
- pedir ajuste
- reenviar para aprovacao

### Fase 2

- integrar Telegram
- ligar respostas do Telegram ao estado da fila
- adicionar template de mensagem de aprovacao

### Fase 3

- integrar publicacao real
- registrar metricas por postagem
- reaproveitar padroes que mais convertem

## Proxima implementacao sugerida

A proxima entrega tecnica natural para este app e:

- adapter de Telegram para notificar itens `awaiting_approval`
- comando ou rotina para consumir feedback do Telegram
- transicao automatica entre `awaiting_approval`, `needs_revision` e `approved`

# Active Incubations

Data: 2026-04-16
Objetivo: registrar backlog inicial dos projetos incubados manualmente quando o pipeline real nao puder rodar por falta de credenciais.

## Como usar

Esse arquivo serve como backlog operacional provisorio e tambem como ponto de partida para futuras rodadas do `Monarch AI`.

Quando o pipeline real estiver configurado com `.env`, essas incubacoes podem ser reprocessadas pela CLI para refinamento.

## Instagram Automation

Prompt base:

`quero um instagram de inteligencia artificial com geracao de posts, legenda e CTA, envio da proposta pelo Telegram para aprovacao ou ajuste antes de publicar, e foco em vender servicos, automacoes e PDFs`

### Objetivo

Construir um perfil de Instagram sobre inteligencia artificial que publique conteudo recorrente com operacao assistida, aprove aprovacao humana via Telegram antes de postar e converta audiencia em venda de servicos, automacoes, projetos e ativos digitais.

### Trilhas

#### 1. Conteudo

- definir avatar principal do perfil
- definir 3 a 5 pilares de conteudo
- criar calendario editorial inicial
- definir formatos base: reels, carrossel, stories e posts de autoridade
- criar criterios para reaproveitamento de conteudo vencedor

#### 2. Oferta

- definir oferta principal de entrada
- definir ofertas secundarias: automacoes, projetos sob medida, PDFs e documentos
- mapear CTA por tipo de conteudo
- decidir quais posts sao de topo, meio e fundo de funil
- criar estrutura de funil simples do Instagram para conversao

#### 3. Automacao-aprovada

- definir pipeline de geracao de post
- gerar legenda e CTA automaticamente
- enviar proposta de postagem via Telegram antes da publicacao
- permitir respostas de aprovacao, rejeicao ou pedido de ajuste
- registrar alteracoes solicitadas antes da publicacao
- publicar apenas depois da aprovacao humana

#### 4. Metricas

- definir metricas principais: alcance, salvamentos, respostas, cliques e conversao
- rastrear posts aprovados vs ajustados
- mapear quais temas geram mais conversa e mais venda
- definir rotina semanal de revisao

### Proximas acoes

1. definir o avatar do perfil
2. escolher 3 pilares de conteudo
3. definir a oferta principal inicial
4. desenhar o fluxo Telegram: gerar -> aprovar/ajustar -> publicar
5. criar lote inicial de 15 ideias de conteudo

Referencia tecnica:

- `docs/instagram-automation-approval-flow.md`

### Criterio de pronto

- perfil com posicionamento claro
- calendario editorial inicial fechado
- pipeline de aprovacao via Telegram desenhado
- CTA conectado a pelo menos uma oferta principal
- primeira fila de conteudo pronta para teste

## Canal Dark

Prompt base:

`quero um canal dark que pegue meus videos, prepare os cortes e faca upload automatico com descricao padrao; alguns videos devem usar descricao focada em views e outros descricao focada em venda de afiliado`

### Objetivo

Construir um canal dark de operacao quase totalmente automatizada, usando videos ja existentes como fonte, preparando cortes e publicando diariamente com descricoes orientadas por estrategia de views ou venda.

### Trilhas

#### 1. Fonte

- mapear onde os videos base ficam armazenados
- definir formato aceito de entrada
- criar criterio de elegibilidade dos videos
- separar videos bons para views dos videos bons para oferta

#### 2. Cortes

- definir regra de corte ou preparacao
- padronizar duracao dos videos
- padronizar titulo base e metadados
- decidir se ha legenda automatica ou nao
- criar lote inicial de cortes prontos

#### 3. Publicacao-automatica

- montar pipeline de upload diario
- definir frequencia de postagem
- automatizar selecao do proximo video
- automatizar titulo, hashtags e agendamento
- registrar falhas de upload e repeticao

#### 4. Descricao

- criar template `views` para videos focados em visualizacao
- criar template `venda` para videos focados em afiliado
- definir regra de escolha entre `views` e `venda`
- decidir se a descricao muda por categoria ou por produto
- padronizar CTA quando houver venda

#### 5. Monetizacao

- definir quais videos podem receber oferta afiliada
- conectar shortlist do `Achadinhos`
- mapear categorias de produtos com mais encaixe
- criar regra para nao exagerar na densidade de venda

### Proximas acoes

1. mapear a pasta ou fonte real dos videos
2. definir criterio de corte
3. criar 2 templates de descricao: `views` e `venda`
4. definir a regra de escolha entre os dois modos
5. montar backlog inicial de 30 uploads

### Criterio de pronto

- pipeline automatico de upload definido
- backlog inicial de cortes preparado
- estrategia de descricao separada em `views` e `venda`
- regra de monetizacao afiliada mapeada
- rotina diaria reproduzivel

## Observacao importante

Essas incubacoes foram registradas manualmente porque o pipeline real da CLI esta bloqueado por falta de configuracao local obrigatoria no `.env`.

Quando as credenciais estiverem prontas, vale rerodar os prompts pela CLI para obter uma versao incubada pelo orchestrator oficial.

## WhatsApp Assessor

Prompt base:

`quero evoluir meu whatsapp-notion-bot para um assessor pessoal via WhatsApp que registre gastos e compromissos, responda consultas, envie lembretes e tenha um painel vendavel por assinatura`

### Objetivo

Transformar o atual `whatsapp-notion-bot`, hoje mais focado em registro de despesas, em um produto de "assessor pessoal" via WhatsApp, com onboarding, operacao recorrente, consultas em linguagem natural, lembretes e painel de acompanhamento.

### Trilhas

#### 1. Onboarding

- criar fluxo de ativacao da conta via WhatsApp
- cadastrar email e senha para painel
- vincular usuario do WhatsApp a conta do sistema
- prever comando para falar com suporte humano

#### 2. Assistente-financeiro

- registrar gastos por texto e audio
- registrar receitas
- suportar transacoes recorrentes
- categorizar automaticamente
- responder saldo, total por periodo e total por categoria

#### 3. Assistente-compromissos

- registrar compromissos por linguagem natural
- registrar afazeres e lembretes
- suportar agenda futura
- integrar com calendario no futuro

#### 4. Consultas

- responder perguntas como:
  - quanto gastei hoje
  - quanto recebi esse mes
  - quais compromissos tenho hoje
  - tenho saldo positivo
- consolidar resposta em linguagem natural pelo WhatsApp

#### 5. Lembretes

- lembrar compromissos do dia
- lembrar eventos proximos
- lembrar contas a pagar e a receber
- enviar resumo diario

#### 6. Painel

- criar painel com visao financeira e de compromissos
- mostrar graficos, categorias e historicos
- permitir configuracao de categorias e preferencias

#### 7. Operacao

- manter webhook confiavel
- manter deduplicacao e rate limiting
- ampliar classificador para intents alem de despesa
- separar intents: gasto, receita, compromisso, consulta, lembrete e suporte

### Proximas acoes

1. redefinir o produto como `WhatsApp Assessor`
2. ampliar o classificador atual para multiplas intents
3. desenhar o fluxo de onboarding e ativacao
4. definir o painel minimo vendavel
5. montar MVP com financas + compromissos + consultas basicas

### Criterio de pronto

- usuario consegue ativar a conta no WhatsApp
- usuario registra gasto, receita e compromisso por linguagem natural
- usuario consulta informacoes no WhatsApp
- usuario recebe lembretes
- painel minimo funciona
- proposta comercial de assinatura fica clara

Referencia tecnica:

- `docs/whatsapp-assessor-product.md`

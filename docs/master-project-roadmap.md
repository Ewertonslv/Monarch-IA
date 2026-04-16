# Master Project Roadmap

Data: 2026-04-15
Escopo: execucao local de todos os projetos do ecossistema antes de qualquer nova subida para servidor ou producao.

## Objetivo

Levar todos os projetos do Hub a um estado minimo completo, com definicao clara de:

- objetivo final
- MVP
- dependencias
- criterio de pronto
- backlog inicial
- ordem de execucao

## Principios

- Tudo fica local ate fecharmos o pacote completo.
- Primeiro estabilizamos a base que destrava os demais projetos.
- Cada projeto precisa sair do estado conceitual e chegar a um fluxo operacional minimo.
- Um projeto nao sera considerado pronto so por ter interface ou repositorio; ele precisa executar seu fluxo principal.

## Status local de implementacao

- Monarch AI: base local fortalecida com roadmap, resumo de execucao e correcoes no fluxo de aprovacao.
- WhatsApp Notion Bot: protecao contra webhook duplicado adicionada no app canonico.
- PDF Factory: scaffold local criado com pipeline, modelos e testes.
- Instagram Automation: scaffold local criado com pesquisa, fila, briefing e checklist de publicacao.
- Canal Dark: scaffold local criado com backlog de pautas e roteiro inicial.
- Achadinhos: scaffold local criado com catalogo, scoring e shortlist.
- TikTok Shop: scaffold local criado para converter shortlist em oferta e validacao inicial.
- Solo Leveling Lab: scaffold local criado com ciclo de experimento e captura de aprendizados.

## Ondas de execucao

### Onda 1: Fundacao operacional

1. Monarch AI
2. WhatsApp Notion Bot

### Onda 2: Produtos internos e automacoes

3. PDF Factory
4. Instagram Automation

### Onda 3: Conteudo e aquisicao

5. Canal Dark
6. Achadinhos
7. TikTok Shop

### Onda 4: Laboratorio autoral

8. Solo Leveling Lab

## Projetos

### 1. Monarch AI

Objetivo final:
Transformar o Monarch AI no sistema operacional da operacao inteira, com hub, cadastros centrais, pipeline multiagente, aprovacoes, execucoes e visao de portfolio.

MVP:
Hub funcional, monarch-core consistente, seed estruturado, visual utilizavel, pipeline de agentes sem travamentos criticos e deploy local reproduzivel.

Dependencias:
Nenhuma.

Criterio de pronto:

- business units, projects, tasks, approvals e roadmap items operam sem inconsistencias
- dashboard reflete o estado real
- pipeline passa por design, aprovacao e implementacao sem quebrar no parser
- implementer roda com contexto reduzido e menor risco de rate limit
- hub tem UX consistente e sem falhas visuais relevantes

Backlog inicial:

- consolidar seed e modelo de portfolio
- revisar fluxo completo do orchestrator
- melhorar implementer para reduzir custo de tokens
- finalizar visoes de projeto, roadmap e aprovacoes
- reforcar observabilidade, healthchecks e feedback de erro

### 2. WhatsApp Notion Bot

Objetivo final:
Receber mensagens pelo WhatsApp, interpretar lancamentos financeiros e registrar tudo no Notion com confiabilidade operacional.

MVP:
Mensagem recebida via webhook, classificacao correta, escrita no Notion, logs minimos e deploy local reproduzivel.

Dependencias:

- infraestrutura base pronta
- dominio/SSL idealmente para producao, mas nao necessario para fechar o pacote local

Criterio de pronto:

- webhook recebe mensagem
- classificador transforma texto em estrutura financeira valida
- escrita no Notion funciona
- erros ficam rastreaveis
- testes principais deixam de depender de mocks excessivos

Backlog inicial:

- revisar integracao Z-API
- reforcar parsing de mensagens
- validar fluxo financeiro ponta a ponta
- melhorar suite de testes
- consolidar configuracao de deploy

### 3. PDF Factory

Objetivo final:
Criar uma linha operacional de ativos digitais vendaveis baseada em briefs e templates.

MVP:
Receber um tema, gerar estrutura, montar PDF final e salvar o ativo em formato pronto para validacao comercial.

Dependencias:

- Monarch AI estavel

Criterio de pronto:

- existe um pipeline repetivel de criacao
- um briefing gera um PDF final consistente
- ha organizacao de templates e saida
- o resultado fica pronto para venda ou teste de mercado

Backlog inicial:

- definir formato padrao de briefing
- criar template base
- montar pipeline de geracao
- validar um primeiro produto
- organizar saidas e metadados

Implementacao local atual:

- pacote canonico criado em `apps/pdf-factory/`
- pipeline inicial de planejamento e renderizacao em markdown
- testes locais adicionados

### 4. Instagram Automation

Objetivo final:
Operar Instagram com fluxo modular de pesquisa, planejamento, fila e publicacao assistida ou segura.

MVP:
Pipeline interno de pesquisa de conteudo, geracao de proposta de post e fila de aprovacao/publicacao.

Dependencias:

- Monarch AI estavel
- regras claras do que pode ser automatizado

Criterio de pronto:

- pesquisa, geracao e fila estao separadas por modulo
- ha um fluxo seguro sem automacao agressiva descontrolada
- o sistema consegue preparar conteudo reutilizavel

Backlog inicial:

- mapear modulos da operacao
- definir entidades e estados do conteudo
- criar fila de conteudo
- integrar aprovacao
- preparar etapa de publicacao assistida

Implementacao local atual:

- pacote canonico criado em `apps/instagram-automation/`
- pipeline de pesquisa para angulos de conteudo
- fila inicial com status `awaiting_approval`
- briefing e checklist de publicacao assistida

### 5. Canal Dark

Objetivo final:
Montar uma maquina de conteudo dark com nicho, pauta, roteiro, producao e distribuicao.

MVP:
Escolher um nicho, gerar backlog inicial e produzir as primeiras pecas usando o novo fluxo.

Dependencias:

- reaproveitamento parcial do stack de geracao de conteudo

Criterio de pronto:

- nicho principal definido
- backlog inicial criado
- pipeline de pauta e roteiro padronizado
- primeiras pecas produzidas no processo novo

Backlog inicial:

- selecionar nicho
- definir formatos
- criar banco de pautas
- criar modelo de roteiro
- fechar etapa de producao inicial

Implementacao local atual:

- pacote canonico criado em `apps/canal-dark/`
- backlog inicial de pautas por tema
- selecao de pauta prioritaria
- roteiro base renderizavel em markdown

### 6. Achadinhos

Objetivo final:
Encontrar, catalogar e pontuar produtos fisicos com potencial de venda.

MVP:
Fluxo que coleta produtos, organiza os dados e produz uma shortlist priorizada.

Dependencias:
Nenhuma tecnica critica.

Criterio de pronto:

- fontes de descoberta definidas
- criterios de scoring definidos
- produtos entram em catalogo com padrao
- shortlist de produtos vencedores sai do sistema

Backlog inicial:

- definir fontes
- definir criterio de scoring
- estruturar catalogo
- criar ranking inicial
- gerar shortlist priorizada

Implementacao local atual:

- pacote canonico criado em `apps/achadinhos/`
- modelos para catalogo e candidatos
- score local com sinais de margem, apelo visual, novidade e demonstracao
- shortlist priorizada com renderizacao em markdown

### 7. TikTok Shop

Objetivo final:
Criar operacao comercial minima para testar venda de produtos fisicos com conteudo.

MVP:
Um produto escolhido, um fluxo minimo de conteudo e uma primeira oferta validavel.

Dependencias:

- Achadinhos

Criterio de pronto:

- produto candidato selecionado
- conteudo de oferta definido
- fluxo comercial minimo documentado
- primeira validacao pratica preparada

Backlog inicial:

- consumir shortlist do Achadinhos
- escolher produto inicial
- estruturar pagina/oferta/script
- alinhar conteudo com proposta comercial
- preparar primeira rodada de validacao

Implementacao local atual:

- pacote canonico criado em `apps/tiktok-shop/`
- conversao de candidato priorizado em angulo de oferta
- roteiro curto de video
- checklist de validacao comercial inicial

### 8. Solo Leveling Lab

Objetivo final:
Transformar o laboratorio autoral em um experimento criativo executavel com entregavel concreto.

MVP:
Um experimento definido com objetivo, formato e primeiro artefato produzido.

Dependencias:
Baixa prioridade em relacao aos projetos operacionais.

Criterio de pronto:

- experimento definido
- escopo claro
- pipeline minimo de producao
- primeiro entregavel pronto

Backlog inicial:

- definir tese criativa
- delimitar escopo do experimento
- escolher formato
- produzir primeiro artefato
- registrar aprendizados e proximo ciclo

Implementacao local atual:

- pacote canonico criado em `apps/solo-leveling-lab/`
- materializacao de tese criativa em experimento
- ciclo inicial de execucao com proximos passos
- renderizacao de plano de experimento e aprendizados

## Ordem de implementacao recomendada

1. Monarch AI
2. WhatsApp Notion Bot
3. PDF Factory
4. Instagram Automation
5. Canal Dark
6. Achadinhos
7. TikTok Shop
8. Solo Leveling Lab

## Regra de liberacao

Nenhum novo deploy ou push de pacote final sera tratado como etapa obrigatoria enquanto:

- o roadmap local nao estiver consolidado
- os projetos das ondas 1 e 2 nao estiverem minimamente executaveis
- o hub nao refletir esse plano com clareza

## Proximo foco

Foco operacional imediato:

1. fechar o Monarch AI localmente
2. fechar o WhatsApp Notion Bot localmente
3. usar o Monarch AI para organizar e destravar os demais projetos

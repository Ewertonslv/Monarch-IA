# Ecosystem Execution Plan

Data: 2026-04-16
Escopo: transformar o Monarch AI no criador e operador central do ecossistema, conectando aquisicao, monetizacao e execucao dos projetos-filhos.

## Visao central

O portfolio nao deve ser tratado como uma colecao de projetos isolados.
O desenho operacional correto e:

- `Monarch AI`: cerebro, criador de projetos, priorizador e coordenador do ecossistema
- `Instagram Automation`: canal de autoridade para IA, distribuicao e venda de servicos/produtos
- `Canal Dark`: canal de volume diario para distribuicao automatizada de cortes
- `Achadinhos`: motor de monetizacao afiliada e selecao de ofertas
- `PDF Factory`: motor de criacao de ativos digitais vendaveis
- `TikTok Shop`: esteira de oferta e validacao comercial de produtos
- `Solo Leveling Lab`: laboratorio autoral e exploratorio
- `WhatsApp Notion Bot`: operacao lateral funcional, util, mas fora do funil principal de aquisicao

## Objetivo macro

Construir um ecossistema em que:

1. o `Monarch AI` gera e estrutura novas ideias por projeto
2. essas ideias viram backlog, roadmap e tarefas rastreaveis
3. `Instagram Automation` vende servicos, PDFs, documentos e projetos
4. `Canal Dark` publica volume diario e gera trafego
5. `Achadinhos` monetiza parte do trafego com afiliados
6. `PDF Factory` entrega produtos proprios vendaveis
7. `TikTok Shop` reaproveita shortlist e validacao comercial

## Mapa do ecossistema

### 1. Coordenacao

- `Monarch AI`
- `monarch-core`
- `monarch-web`

### 2. Aquisicao

- `Instagram Automation`
- `Canal Dark`

### 3. Monetizacao

- `PDF Factory`
- `Achadinhos`
- `TikTok Shop`

### 4. Exploracao

- `Solo Leveling Lab`

### 5. Operacao paralela

- `WhatsApp Notion Bot`

## Papel do Monarch AI

O `Monarch AI` deve assumir 3 modos principais.

### Modo 1: Ideacao

Objetivo:
- gerar ideias por projeto
- explorar oportunidades
- produzir opcoes priorizadas

Pipeline recomendado:
- `discovery`
- `prioritization`
- `architecture`
- `planning`

Saida esperada:
- lista de ideias
- top ideias priorizadas
- riscos
- proposta de backlog inicial

### Modo 2: Incubacao

Objetivo:
- promover a melhor ideia a projeto operacional

Saida esperada:
- projeto criado
- roadmap inicial
- tarefas iniciais
- responsaveis sugeridos
- criterio de pronto

### Modo 3: Execucao

Objetivo:
- tocar implementacao de itens ja aprovados

Saida esperada:
- execucao de backlog
- aprovacao
- revisao
- atualizacao do Hub

## Formula de execucao por projeto

Cada projeto-filho deve seguir o mesmo ciclo:

1. gerar ideias
2. priorizar top 3
3. escolher top 1
4. criar backlog inicial
5. registrar no Hub
6. executar em ondas curtas
7. medir resultado
8. alimentar proxima rodada

## Projetos

### Monarch AI

Objetivo:
ser o criador de projetos e sistema operacional do portfolio

Entrada:
- ideias de negocio
- feedback dos projetos-filhos
- prompts de descoberta

Saida:
- projetos criados
- backlog inicial
- roadmap
- tarefas
- visao consolidada do portfolio

O que falta:
- modo explicito de ideacao/incubacao por projeto
- modularizacao do `monarch-web`
- reduzir hardcodes no Hub
- reforcar integracao `orchestrator <-> core <-> web`
- ampliar testes do nucleo
- transformar o Hub em painel operacional

Definicao de pronto:
- consegue gerar ideias por projeto
- consegue promover ideia para backlog
- consegue acompanhar execucao por projeto
- consegue refletir no Hub o estado real do ecossistema

### Instagram Automation

Objetivo:
operar um Instagram focado em inteligencia artificial para gerar autoridade e vendas

Entrada:
- temas de IA
- dores do publico
- ofertas de servicos
- ativos do `PDF Factory`

Saida:
- fila de posts
- pilares de conteudo
- calendarios
- CTAs
- ofertas conectadas ao perfil

Monetizacao:
- servicos
- automacoes
- projetos
- consultoria
- PDFs
- documentos

O que falta:
- definir avatar principal
- definir 3 a 5 pilares de conteudo
- definir ofertas principais
- definir funil de CTA
- integrar a fila local ao Hub
- transformar scaffold em operacao recorrente

Definicao de pronto:
- calendario editorial minimo fechado
- fila funcionando
- ofertas conectadas aos conteudos
- primeira esteira de conversao montada

### Canal Dark

Objetivo:
subir cortes diariamente com o maximo de automacao viavel e gerar volume

Entrada:
- videos fonte
- cortes brutos
- regras de selecao
- templates de metadata
- shortlist de ofertas do `Achadinhos`

Saida:
- cortes prontos para postagem
- rotina diaria
- backlog de conteudo
- pontos de monetizacao

Monetizacao:
- trafego
- afiliado
- possivel direcionamento para outras ofertas

O que falta:
- definir fonte dos videos
- definir criterio de corte
- definir pipeline diario
- definir plataforma e frequencia
- automatizar titulo, descricao e postagem
- definir regra de encaixe de afiliado

Definicao de pronto:
- pelo menos um pipeline reproduzivel de postagem diaria
- backlog inicial de videos/cortes
- pontos de monetizacao mapeados

### Achadinhos

Objetivo:
selecionar produtos afiliados com potencial real de conversao

Entrada:
- catálogos
- programas de afiliado
- nichos alvo
- sinais de margem, novidade e apelo visual

Saida:
- catalogo
- shortlist priorizada
- score
- argumentos de venda
- produtos recomendados por contexto

Monetizacao:
- comissao afiliada

O que falta:
- definir programas de afiliado
- definir nichos prioritarios
- preencher catalogo com produtos reais
- calibrar scoring
- conectar saida ao `Canal Dark`
- eventualmente conectar saida ao `TikTok Shop`

Definicao de pronto:
- shortlist real gerada a partir de catalogo real
- ranking confiavel para testes
- produtos conectados ao conteudo

### PDF Factory

Objetivo:
gerar produtos digitais e documentos vendaveis

Entrada:
- dores do publico
- temas de IA
- demandas comerciais
- briefing

Saida:
- PDFs
- e-books
- guias
- playbooks
- propostas
- documentos

Monetizacao:
- venda direta
- apoio a venda de servicos

O que falta:
- definir linha inicial de produtos
- definir publico-alvo por produto
- fechar template comercial base
- garantir saida final vendavel
- conectar com CTA do `Instagram Automation`

Definicao de pronto:
- primeiro ativo comercial validavel entregue
- pipeline repetivel funcionando
- acoplamento com canal de venda definido

### TikTok Shop

Objetivo:
transformar shortlist de produtos em oferta comercial validavel

Entrada:
- shortlist do `Achadinhos`
- copy curta
- ganchos de oferta

Saida:
- estrutura de oferta
- checklist comercial
- roteiro curto
- validacao inicial

Monetizacao:
- venda de produto
- venda afiliada

O que falta:
- integrar formalmente com `Achadinhos`
- escolher primeiro produto
- montar primeira oferta
- definir criterio de validacao

Definicao de pronto:
- primeiro produto candidato transformado em oferta testavel

### Solo Leveling Lab

Objetivo:
servir como laboratorio autoral para experimentos criativos

Entrada:
- teses criativas
- ideias autorais
- formatos de experimento

Saida:
- experimentos
- aprendizados
- artefatos criativos

Monetizacao:
- indireta no inicio

O que falta:
- definir primeiro artefato concreto
- definir tese
- reduzir abstracao e aumentar tangibilidade

Definicao de pronto:
- primeiro experimento concluido e registrado

### WhatsApp Notion Bot

Objetivo:
registrar gastos via WhatsApp no Notion com confiabilidade

Entrada:
- mensagem via webhook

Saida:
- classificacao
- registro no Notion
- confirmacao de volta

Monetizacao:
- nenhuma direta dentro do funil principal

O que falta:
- validar integracao real ponta a ponta
- reforcar testes menos dependentes de mocks
- revisar deploy local

Definicao de pronto:
- fluxo webhook -> classificacao -> notion -> confirmacao validado

## Ordem de execucao

### Onda 1: Fundacao do criador de projetos

1. `Monarch AI`
2. `monarch-core`
3. `monarch-web`

Meta:
- habilitar o Monarch como incubadora de ideias e backlog

### Onda 2: Primeira monetizacao propria

4. `PDF Factory`
5. `Instagram Automation`

Meta:
- criar produto + canal de venda

### Onda 3: Volume e afiliado

6. `Canal Dark`
7. `Achadinhos`
8. `TikTok Shop`

Meta:
- construir rotina de volume e acoplar monetizacao afiliada

### Onda 4: Exploracao e paralelos

9. `Solo Leveling Lab`
10. `WhatsApp Notion Bot`

Meta:
- fechar exploracao autoral e estabilizar operacao paralela

## Plano de execucao em 30 dias

### Semana 1

Foco:
- `Monarch AI`
- `monarch-core`
- `monarch-web`

Entregaveis:
- definir modo de ideacao por projeto
- padronizar criacao de backlog inicial por tipo
- revisar fluxo de projeto/ideia/tarefa no Hub
- listar friccoes reais do orchestrator

### Semana 2

Foco:
- `Instagram Automation`
- `PDF Factory`

Entregaveis:
- avatar e pilares do Instagram
- ofertas principais
- primeira linha de PDFs/produtos
- acoplamento entre conteudo e CTA

### Semana 3

Foco:
- `Canal Dark`
- `Achadinhos`

Entregaveis:
- pipeline de cortes
- criterio de selecao
- primeiros produtos afiliados shortlistados
- regra de encaixe de produto nos videos

### Semana 4

Foco:
- `TikTok Shop`
- `Solo Leveling Lab`
- `WhatsApp Notion Bot`

Entregaveis:
- primeira oferta validavel do TikTok Shop
- primeiro experimento autoral concreto
- validacao real do bot ponta a ponta

## Proximas acoes imediatas

1. consolidar o `Monarch AI` como incubadora por projeto
2. transformar o `Instagram Automation` em canal de autoridade e venda
3. fechar o primeiro ativo comercial do `PDF Factory`
4. estruturar o pipeline diario do `Canal Dark`
5. abastecer o `Achadinhos` com shortlist real
6. conectar `Achadinhos` ao `Canal Dark` e ao `TikTok Shop`

## Regra de decisao

Um projeto-filho so deve ser tratado como realmente avancado quando tiver:

- proposta clara
- backlog operacional
- fluxo principal reproduzivel
- saida concreta
- criterio minimo de monetizacao ou validacao

## Leitura final

O foco principal nao e "ter muitos projetos".
O foco principal e fazer o `Monarch AI` operar como sistema de criacao, incubacao e coordenacao de projetos, enquanto os projetos-filhos deixam de ser apenas scaffolds e passam a ser operacoes reais conectadas entre si.

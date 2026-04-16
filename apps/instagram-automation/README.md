# Instagram Automation

Pipeline local para operar Instagram de forma modular e segura, separando:

- pesquisa de sinais e referencias
- geracao de propostas de conteudo
- fila de aprovacao
- checklist de publicacao assistida

Objetivo desta fase:
tirar o projeto do campo conceitual e deixá-lo com uma base concreta reutilizavel
no ecossistema do Monarch.

## Modulos

- `instagram_automation.models`
  Estruturas de dados do pipeline.
- `instagram_automation.pipeline`
  Funcoes para transformar pesquisa em fila pronta para aprovacao.

## Fluxo atual

1. Consolidar sinais de pesquisa em angulos de conteudo
2. Selecionar a melhor proposta para fila
3. Gerar briefing com legenda, CTA e hashtags
4. Gerar checklist de publicacao assistida

## Proximo passo

Integrar a fila ao Hub do Monarch para que cada item possa virar tarefa,
aprovacao e execucao rastreavel.

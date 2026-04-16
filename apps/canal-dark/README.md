# Canal Dark

Pipeline local para estruturar uma maquina de conteudo dark com:

- definicao de nicho
- backlog inicial de pautas
- esqueleto de roteiro
- preparacao para producao em lote

Objetivo desta fase:
tirar o projeto do estado abstrato e gerar uma base concreta de pautas e roteiros
reutilizaveis dentro do ecossistema.

## Modulos

- `canal_dark.models`
  Estruturas de nicho, pauta e roteiro.
- `canal_dark.pipeline`
  Funcoes para transformar uma tese de nicho em backlog e script inicial.

## Fluxo atual

1. Definir nicho e objetivo editorial
2. Gerar backlog inicial de pautas
3. Escolher pauta prioritaria
4. Montar roteiro base para primeira producao

## Proximo passo

Conectar as pautas e roteiros ao `Instagram Automation` e ao Hub do Monarch,
para que a producao vire fila de execucao rastreavel.

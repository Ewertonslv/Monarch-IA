# Achadinhos

Pipeline local para descoberta, catalogacao e priorizacao de produtos fisicos.

Objetivo desta fase:
transformar o projeto em uma maquina inicial de shortlist, capaz de receber
produtos candidatos, pontuar sinais de potencial e priorizar o que merece teste.

## Modulos

- `achadinhos.models`
  Estruturas de dados para fontes, candidatos e shortlist.
- `achadinhos.pipeline`
  Funcoes para normalizar catalogo, pontuar e priorizar oportunidades.

## Fluxo atual

1. Receber produtos candidatos de fontes distintas
2. Normalizar os dados minimos para catalogo
3. Aplicar score com base em margem, apelo visual, novidade e facilidade de demonstracao
4. Gerar shortlist priorizada para validacao comercial

## Proximo passo

Conectar a shortlist gerada aqui ao projeto `TikTok Shop`, para transformar
os melhores candidatos em roteiros de oferta e ciclos de validacao.

# TikTok Shop

Pipeline local para transformar produtos priorizados em uma proposta comercial
minima pronta para validacao.

Objetivo desta fase:
receber um candidato priorizado, montar angulo de oferta, roteiro curto de video
e checklist de validacao comercial.

## Modulos

- `tiktok_shop.models`
  Estruturas para oferta, criativo e plano de validacao.
- `tiktok_shop.pipeline`
  Funcoes para converter shortlist em um playbook inicial de teste.

## Fluxo atual

1. Receber um produto priorizado
2. Escolher um angulo de oferta simples
3. Montar roteiro curto de conteudo
4. Definir checklist de validacao da primeira oferta

## Proximo passo

Conectar o pipeline ao `Achadinhos` e ao Hub do Monarch, para que cada oferta
apareca como experimento rastreavel com execucao e feedback.

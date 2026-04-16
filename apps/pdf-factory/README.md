# PDF Factory

Pipeline local para transformar um briefing em um ativo digital estruturado e exportavel.

## Escopo atual

MVP inicial:

- receber um briefing estruturado
- gerar um plano de documento
- renderizar o ativo em Markdown
- definir nome de saida consistente

## Estrutura

- `pdf_factory/models.py`: modelos de entrada e saida
- `pdf_factory/pipeline.py`: pipeline principal
- `tests/test_pipeline.py`: testes unitarios do fluxo base

## Proximo passo

- adicionar templates por nicho
- gerar HTML/PDF a partir do Markdown
- acoplar esse fluxo ao Monarch AI

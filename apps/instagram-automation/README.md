# Instagram Automation

CLI para pesquisa, fila, revisao e aprovacao de conteudo.

## Fluxo atual

1. gerar proposta de conteudo
2. colocar na fila de aprovacao
3. aprovar, rejeitar ou pedir ajuste
4. reenviar para aprovacao
5. publicar depois do ok final

## Uso

```bash
pip install -r requirements.txt
python -m instagram_automation research --niche "instagram de IA" --objective "gerar leads"
python -m instagram_automation queue
python -m instagram_automation brief --index 1
python -m instagram_automation request-changes 1 --note "deixar o CTA mais claro"
python -m instagram_automation feedback 1
python -m instagram_automation requeue 1 --note "CTA ajustado"
python -m instagram_automation approve 1
```

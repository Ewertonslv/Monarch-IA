# PDF Factory

CLI para gerar documentos profissionais: Markdown, HTML e PDF.

## Uso

```bash
pip install -r requirements.txt
python -m pdf_factory run --title "Titulo" --audience "publico"
python -m pdf_factory run-file briefing.json
```

## Templates

| Template | Estilo |
|---|---|
| `minimal` | Clean, roxo/branco |
| `sales` | Quente, laranja/serifado |
| `dark` | Dark mode |

## Formatos

`--output-format md|html|pdf|all`

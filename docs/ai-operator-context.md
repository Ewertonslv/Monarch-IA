# AI Operator Context

Data: 2026-04-16
Objetivo: servir como arquivo de leitura inicial para qualquer IA que entrar neste repositorio.

## Como usar este arquivo

Antes de pedir qualquer trabalho para uma IA neste projeto, use algo como:

`Leia primeiro docs/ai-operator-context.md e use esse contexto antes de agir.`

Esse arquivo existe para alinhar entendimento sobre:

- o que e o `Monarch AI`
- o papel de cada projeto-filho
- como os projetos se conectam
- qual fluxo operacional deve ser respeitado

## Regra principal do ecossistema

`Monarch AI` nao e apenas mais um app.

Ele e o criador de projetos, incubadora de ideias e coordenador do ecossistema.

Os outros projetos nao devem ser tratados como iniciativas isoladas. Eles fazem parte de um sistema maior.

## Regra de operacao

O fluxo de desenvolvimento e operacao principal e `CLI-first`.

Isso significa:

- toda a parte de desenvolvimento, ideacao, incubacao e execucao deve acontecer via CLI
- o `Hub` nao e a interface principal de desenvolvimento
- o `Hub` existe principalmente para mostrar dados, status, sinais e ajudar em tomada de decisao
- a IA nao deve tentar mover o fluxo principal para o Hub sem pedido explicito

## Ferramentas externas disponiveis neste ambiente

Este ambiente tambem pode ter acesso a MCPs/ferramentas auxiliares importantes.

As principais mencionadas ate agora sao:

- pesquisa na internet
- geracao de imagem

Como qualquer IA deve usar isso:

- usar pesquisa na internet quando precisar validar tendencias, referencias, nichos, ideias, concorrencia ou inspiracoes atuais
- usar geracao de imagem quando fizer sentido criar artes, variacoes visuais, conceitos ou ativos criativos
- essas ferramentas complementam o trabalho do `Monarch`, mas nao substituem a regra `CLI-first`
- a IA deve usar essas capacidades como apoio de ideacao, criacao e validacao, especialmente em projetos de conteudo, oferta e ativos visuais

## Requisitos minimos para rodar o pipeline real do Monarch

Para rodar o pipeline real pela CLI, o ambiente local precisa de configuracao valida.

No estado atual, os principais campos exigidos sao:

- `ANTHROPIC_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

Sem isso:

- a CLI de incubacao e ideacao nao roda de ponta a ponta
- a IA ainda pode documentar, planejar e estruturar backlog localmente
- mas a execucao real do orchestrator fica bloqueada

Referencia rapida:

- usar `.env.example` como base

## Papel de cada projeto

### Monarch AI

Finalidade:
- criar ideias
- incubar projetos
- priorizar portfolio
- transformar ideia em backlog
- coordenar execucao do ecossistema

Modos principais:
- `execution`: implementa
- `ideation`: gera opcoes e prioriza
- `incubation`: cria backlog inicial e proximas acoes

## Pipeline de agentes do Monarch

O `Monarch AI` opera por pipeline multiagente.

A ordem base atual do orchestrator e:

1. `discovery`
2. `prioritization`
3. `architecture`
4. `planning`
5. `devils_advocate`
6. `implementer`
7. `testing`
8. `reviewer`
9. `security`
10. `deploy`
11. `documentation`
12. `observability`

Nem todos os modos percorrem o pipeline inteiro.

### O que cada agente faz

`discovery`
- interpreta o pedido
- levanta contexto
- identifica necessidade real, escopo e areas afetadas

`prioritization`
- classifica importancia, urgencia e ordem de ataque
- ajuda a definir o que deve vir primeiro

`architecture`
- propoe abordagem tecnica ou estrutural
- organiza componentes, fluxo e decisoes principais

`planning`
- transforma a direcao em plano e backlog inicial
- gera passos executaveis

`devils_advocate`
- questiona o plano
- aponta riscos, lacunas e ajustes antes de seguir
- pode forcar nova rodada de `architecture` + `planning`

`implementer`
- implementa a mudanca quando o modo e de execucao

`testing`
- valida comportamento
- executa ou orienta testes para confirmar que a entrega funciona

`reviewer`
- revisa qualidade, comportamento e risco de regressao

`security`
- verifica riscos de seguranca e pontos sensiveis

`deploy`
- prepara entrega ou fechamento operacional da execucao

`documentation`
- registra o que precisa ficar documentado apos a entrega

`observability`
- pensa em logs, sinais, monitoramento e diagnostico

### Como o pipeline muda por modo

`ideation`
- roda: `discovery -> prioritization -> architecture -> planning -> devils_advocate`
- para antes da implementacao
- saida esperada: ideias, caminhos priorizados, riscos e direcao

`incubation`
- roda: `discovery -> prioritization -> architecture -> planning -> devils_advocate`
- para antes da implementacao
- saida esperada: backlog inicial, proximas acoes, criterio de pronto e estrutura do projeto

`execution`
- roda o pipeline completo
- passa por aprovacoes humanas depois do planejamento e depois da implementacao
- inclui implementacao, testes, revisao, seguranca, deploy, documentacao e observabilidade

### Regra importante para qualquer IA

Ao trabalhar neste repositorio, a IA deve entender que o pedido nao entra direto em implementacao.

O fluxo correto do `Monarch` e:

- entender
- priorizar
- estruturar
- planejar
- desafiar o plano
- so depois implementar, se o modo for `execution`

Se o pedido for de ideacao ou incubacao, a IA nao deve tentar codar. Ela deve respeitar o corte do pipeline e entregar saida de planejamento.

### Instagram Automation

Finalidade:
- operar um Instagram sobre inteligencia artificial
- publicar conteudo recorrente
- gerar autoridade
- vender servicos, projetos, PDFs e documentos

Papel no ecossistema:
- canal de aquisicao e conversao

Trilhas principais:
- `conteudo`
- `oferta`
- `automacao-aprovada`
- `metricas`

Regra operacional:
- a automacao do Instagram deve ser assistida
- a IA pode gerar post, legenda, CTA e proposta de publicacao
- antes de publicar, o ideal e enviar a proposta no Telegram para aprovacao humana
- o usuario pode aprovar, rejeitar ou pedir ajuste
- esse projeto nao deve assumir publicacao 100% automatica como fluxo principal

Referencia tecnica:

- `docs/instagram-automation-approval-flow.md`

### Canal Dark

Finalidade:
- publicar cortes de video diariamente com automacao
- gerar volume de distribuicao
- encaixar monetizacao afiliada em parte dos videos

Papel no ecossistema:
- canal de volume e distribuicao

Trilhas principais:
- `fonte`
- `cortes`
- `publicacao-automatica`
- `descricao`
- `monetizacao`

Regra operacional:
- o Canal Dark deve operar com o maximo possivel de automacao
- o fluxo principal e pegar videos ja existentes, preparar os cortes e fazer upload
- nao depende de aprovacao humana post a post como regra principal
- a descricao pode seguir pelo menos duas estrategias:
  - `views`: descricao simples para maximizar visualizacao
  - `venda`: descricao orientada a empurrar uma oferta afiliada
- a IA deve tratar a escolha de descricao como parte do pipeline do canal

### Achadinhos

Finalidade:
- selecionar produtos afiliados com potencial de conversao
- abastecer videos, conteudos e ofertas

Papel no ecossistema:
- motor de monetizacao afiliada

Trilhas principais:
- `catalogo`
- `scoring`
- `ofertas`
- `integracoes`

### PDF Factory

Finalidade:
- criar produtos digitais e documentos vendaveis
- apoiar monetizacao do Instagram e de outras frentes

Papel no ecossistema:
- motor de produto proprio

Trilhas principais:
- `produto`
- `template`
- `geracao`
- `entrega`

### TikTok Shop

Finalidade:
- transformar shortlist de produtos em ofertas comercialmente validaveis

Papel no ecossistema:
- extensao de monetizacao orientada a oferta

Trilhas principais:
- `shortlist`
- `oferta`
- `conteudo`
- `validacao`

### Solo Leveling Lab

Finalidade:
- testar ideias criativas e autorais
- transformar tese em experimento tangivel

Papel no ecossistema:
- laboratorio exploratorio

Trilhas principais:
- `tese`
- `experimento`
- `artefato`
- `aprendizado`

### WhatsApp Notion Bot

Finalidade:
- evoluir de bot de gastos para um assessor pessoal via WhatsApp
- registrar gastos e compromissos
- responder consultas em linguagem natural
- enviar lembretes e resumos
- oferecer painel e potencial de produto vendavel por assinatura

Papel no ecossistema:
- produto potencialmente vendavel e operacao utilitaria paralela

Trilhas principais:
- `onboarding`
- `assistente-financeiro`
- `assistente-compromissos`
- `consultas`
- `lembretes`
- `painel`
- `operacao`

Regra operacional:
- a referencia funcional aqui e a ideia de um "assessor" que vive no WhatsApp
- o projeto nao deve ficar limitado a registrar despesas
- ele deve evoluir para um fluxo de ativacao, uso recorrente, consultas e lembretes
- isso pode se tornar uma oferta vendavel por assinatura

Referencia tecnica:

- `docs/whatsapp-assessor-product.md`

## Como os projetos se conectam

Estrutura correta:

- `Monarch AI` coordena, cria e prioriza
- `Instagram Automation` gera autoridade e vendas
- `Canal Dark` gera volume
- `Achadinhos` monetiza parte do volume com afiliados
- `PDF Factory` gera produtos proprios para vender
- `TikTok Shop` aproveita shortlist e cria ofertas testaveis
- `Solo Leveling Lab` explora novas frentes
- `WhatsApp Notion Bot` fica como operacao utilitaria lateral

## Diferenca operacional importante entre Instagram e Canal Dark

Essa diferenca deve ser respeitada por qualquer IA:

`Instagram Automation`
- automacao assistida
- foco em qualidade, posicionamento, CTA e venda
- idealmente com aprovacao via Telegram antes da postagem

`Canal Dark`
- automacao quase total
- foco em volume, consistencia e upload
- descricoes podem alternar entre modo `views` e modo `venda`

## Como a IA deve agir neste repositorio

Ao receber um pedido:

1. identificar se o trabalho e de `execution`, `ideation` ou `incubation`
2. identificar qual projeto do ecossistema e o alvo principal
3. respeitar a logica `CLI-first`
4. considerar como esse projeto se conecta com os demais
5. evitar tratar os projetos como silos independentes

## Regras de interpretacao

Se o pedido falar de:

- Instagram sobre IA, venda de servicos, conteudo e autoridade -> `Instagram Automation`
- cortes diarios, videos, publicacao em escala -> `Canal Dark`
- afiliado, shortlist, produtos, ofertas de produto -> `Achadinhos` ou `TikTok Shop`
- PDFs, documentos, guias, playbooks -> `PDF Factory`
- incubar, priorizar portfolio, criar projetos -> `Monarch AI`
- experimento criativo autoral -> `Solo Leveling Lab`
- gastos por WhatsApp e Notion -> `WhatsApp Notion Bot`

## Resultado esperado de uma boa IA aqui

Uma boa IA neste repositorio deve:

- entender que existe um ecossistema e nao apenas apps separados
- usar o `Monarch AI` como criador e coordenador
- respeitar o fluxo por CLI
- saber qual a finalidade de cada projeto
- propor backlog e proximas acoes coerentes com o papel de cada frente

## Arquivos relacionados

Para mais contexto, vale ler tambem:

- `README.md`
- `docs/active-incubations.md`
- `docs/instagram-automation-approval-flow.md`
- `docs/whatsapp-assessor-product.md`
- `docs/ecosystem-execution-plan.md`
- `docs/master-project-roadmap.md`

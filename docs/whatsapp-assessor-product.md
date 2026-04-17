# WhatsApp Assessor Product

Data: 2026-04-16
Objetivo: especificar a evolucao do `whatsapp-notion-bot` para um produto de "assessor pessoal" via WhatsApp.

## Origem da ideia

Referencia funcional analisada:

- [Meu Assessor](https://www.meuassessor.com/)

Leitura principal da proposta:

- ativacao da conta pelo WhatsApp
- assistente operando 24h no WhatsApp
- registro financeiro por linguagem natural
- organizacao de compromissos
- consultas e respostas no proprio WhatsApp
- lembretes
- painel para acompanhamento
- modelo vendavel por assinatura

## Regra importante

O objetivo aqui nao e copiar o site.

O objetivo e capturar a proposta funcional do "assessor" e adaptar isso ao seu projeto e ao seu stack.

## Estado atual do projeto

Hoje o `whatsapp-notion-bot` ja tem base para:

- receber webhook
- extrair mensagem
- classificar despesa
- gravar no Notion
- responder confirmacao no WhatsApp

Ou seja:

ele ja funciona como um bot de registro de gastos,
mas ainda nao funciona como um "assessor" completo.

## Nova definicao de produto

Nome funcional sugerido:

- `WhatsApp Assessor`

Proposta:

um assistente pessoal via WhatsApp que entende linguagem natural para organizar:

- financas
- compromissos
- lembretes
- consultas

e que entrega:

- operacao no WhatsApp
- painel de acompanhamento
- potencial de venda em assinatura

## Capacidades principais

### 1. Onboarding e ativacao

- iniciar conta via WhatsApp
- cadastrar email
- criar senha
- habilitar acesso ao painel
- prever transferencia para suporte humano

### 2. Financeiro

- registrar gastos
- registrar receitas
- registrar recorrencias
- categorizar automaticamente
- responder saldo e totais
- responder gasto por categoria

### 3. Compromissos

- registrar reunioes, consultas e eventos
- lembrar compromissos futuros
- responder agenda do dia ou semana

### 4. Consultas em linguagem natural

Exemplos:

- quanto gastei hoje
- quanto recebi esse mes
- tenho saldo positivo
- quais compromissos tenho hoje
- quanto gastei em alimentacao

### 5. Lembretes e resumos

- lembrete diario
- lembrete de evento proximo
- resumo do dia
- contas a pagar e a receber

### 6. Painel

- fluxo de caixa
- historico de registros
- categorias
- agenda e compromissos
- configuracoes basicas do usuario

## Arquitetura funcional sugerida

### Camada 1. Entrada

- webhook do WhatsApp
- normalizacao de payload
- deduplicacao
- rate limiting

### Camada 2. Roteamento de intencao

O classificador atual precisa evoluir de:

- apenas `expense`

para algo como:

- `expense`
- `income`
- `commitment`
- `query`
- `reminder`
- `support`

### Camada 3. Servicos de dominio

- financeiro
- compromissos
- consultas
- lembretes
- onboarding

### Camada 4. Persistencia

Possibilidades:

- continuar com Notion no inicio
- ou migrar parte da persistencia para backend proprio se o produto crescer

### Camada 5. Saida

- confirmacoes no WhatsApp
- respostas de consulta
- lembretes ativos
- painel

## MVP recomendado

Fase 1:

- onboarding simples
- gastos
- receitas
- compromissos
- consultas basicas

Fase 2:

- lembretes
- resumo diario
- painel minimo

Fase 3:

- conta compartilhada
- integracao com agenda
- planos e monetizacao

## Proxima implementacao tecnica sugerida

1. trocar o classificador atual de despesa por classificador de intents
2. criar schema de mensagem de entrada normalizada
3. separar handlers por intent
4. manter o fluxo de confirmacao pelo WhatsApp
5. definir o painel minimo

## Valor comercial

Esse projeto pode deixar de ser apenas utilitario interno e virar produto.

Possiveis angulos de venda:

- assessor financeiro no WhatsApp
- organizador de compromissos no WhatsApp
- assistente pessoal via WhatsApp
- painel simples + WhatsApp como diferencial

## Ligacao com o ecossistema

Esse produto pode se conectar com:

- `Instagram Automation` para venda de assinatura
- `PDF Factory` para materiais comerciais, onboarding e suporte
- `Monarch AI` para ideacao, backlog e evolucao do produto

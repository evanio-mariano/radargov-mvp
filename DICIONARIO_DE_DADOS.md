# Dicionario de dados - RadarGov (Sprint 1)

## Fonte

**Execucao da Despesa** - Portal da Transparencia do Governo Federal
Pagina de download: https://portaldatransparencia.gov.br/download-de-dados/despesas-execucao
Dicionario oficial: https://portaldatransparencia.gov.br/pagina-interna/603453-dicionario-de-dados-execucao-da-despesa

Arquivo mensal consolidado, em CSV, com a execucao orcamentaria e financeira
das despesas do Poder Executivo federal.

Formato do arquivo (confirmado em set/2026):
- um ZIP por mes; dentro, um unico CSV
- separador `;`  |  codificacao `latin-1`  |  separador decimal `,`
- URL de download direto: `https://portaldatransparencia.gov.br/download-de-dados/despesas-execucao/AAAAMM`

## Campos usados no MVP

| Campo no CSV | Nome interno | Uso |
|---|---|---|
| Código Órgão Superior | `cod_orgao` | chave de classificacao orgao -> area (numero estavel) |
| Nome Órgão Superior | `orgao` | nome para leitura (o Portal corta o texto em 43 caracteres) |
| Nome Função | `funcao` | detalhe da despesa dentro da area |
| Valor Pago (R$) | `valor` | valor efetivamente desembolsado no mes |
| (mes do arquivo) | `ano_mes` | eixo temporal (formato AAAA-MM) |

O arquivo traz tres medidas de gasto: **Valor Empenhado** (verba comprometida),
**Valor Liquidado** (servico/produto entregue e conferido) e **Valor Pago**
(desembolso efetivo). O MVP usa **Valor Pago** por ser a medida mais direta do
gasto realizado. Nao existe coluna "Orcamento Realizado" neste arquivo.

## Granularidade

Uma linha por combinacao **mes x area x orgao x funcao**, com o `Valor Pago` somado.

## Recorte aplicado

- Janela temporal: ultimos N meses (config `MESES_JANELA`; MVP validado com 6).
- Areas de interesse: saude, educacao, infraestrutura (config `AREAS`).
- Classificacao orgao -> area: tabela `de_para_orgao_area.csv`, por **codigo do
  orgao superior**. Codigos usados no MVP:
  - saude: 36000 (Ministerio da Saude)
  - educacao: 26000 (Ministerio da Educacao)
  - infraestrutura: 39000 (Transportes), 56000 (Cidades),
    53000 (Integracao e Desenvolvimento Regional), 68000 (Portos e Aeroportos)
- Escopo: apenas despesas diretas da Uniao (Poder Executivo federal).
  Ficam de fora transferencias a estados/municipios, emendas e outros poderes.

## Fonte alternativa (nao usada como principal nesta fase)

API de Dados do Portal da Transparencia
- Base: `https://api.portaldatransparencia.gov.br/api-de-dados`
- Cabecalho de autenticacao: `chave-api-dados: <token>`
- Cadastro do token (gratuito, requer login Gov.br nivel Prata/Ouro ou CPF+senha
  com verificacao em duas etapas): https://portaldatransparencia.gov.br/api-de-dados/cadastrar-email
- Limites (confirmados set/2026): 400 requisicoes/min (06h-23h59), 700/min (00h-05h59);
  uso acima disso suspende a chave por 8h.
- Endpoint relevante: `/despesas/por-orgao` (parametros `codigoOrgao`, `mesAno`, `pagina`)
- Limitacoes: cota de requisicoes por minuto e paginacao; melhor para consultas pontuais
  do que para carga de periodo completo. Por isso o MVP usa os arquivos mensais.

## Ranking de favorecidos (Sprint 2 - escopo restrito a infraestrutura)

Fonte: endpoint `GET /api-de-dados/despesas/recursos-recebidos` da API do Portal
(mesma API de Dados acima, mesma chave e mesmos limites de requisicao).

Diferente do arquivo de Execucao da Despesa, este endpoint identifica o
**favorecido** (quem recebeu o pagamento): nome, CPF/CNPJ, orgao, mes e valor.
Nao existe parametro de ordenacao por valor - para obter um ranking correto e
preciso percorrer **todas** as paginas do periodo/orgao (paginas de 15
registros cada) e ordenar localmente.

**Medicao de volume por area (agosto/2026, 1 mes, todos os orgaos da area):**

| Area | Paginas estimadas/mes | Registros estimados/mes |
|---|---|---|
| Infraestrutura (4 orgaos) | ~600-650 | ~9.500 |
| Saude (1 orgao) | ~2.500-3.000 | ~37.500-45.000 |
| Educacao (1 orgao) | ~16.000-32.000 | ~240.000-480.000 |

Saude e educacao tem volume muito maior porque envolvem pagamento a um grande
numero de pessoas fisicas (profissionais de saude, bolsistas, escolas e
municipios via FUNDEB/PNAE) - inviavel de coletar de forma completa dentro do
prazo do MVP. **Por isso, o ranking de favorecidos no MVP cobre apenas a area
infraestrutura**, onde o volume e baixo o suficiente para uma coleta completa
e correta (~61 mil registros brutos nos 6 meses da janela, sem atingir o
limite de seguranca do script). Saude e educacao ficam registradas como
evolucao futura do produto.

Implementacao: `src/coleta_favorecidos.py` (producao, cobre todos os orgaos
da area configurada em `config.FAV_AREA`, na janela de `config.MESES_JANELA`)
e `src/coleta_favorecidos_piloto.py` (usado para medir o volume por
orgao/mes antes de decidir o escopo).

Achado metodologico: os maiores favorecidos de infraestrutura sao bancos
publicos federais (Caixa Economica Federal, BNDES, Banco do Nordeste, Banco
do Brasil, Banco da Amazonia) atuando como agentes financeiros de programas
(habitacao, financiamento a empreendimentos, fundos constitucionais de
desenvolvimento regional) - nao empreiteiras diretamente. Alguns registros
aparecem como "SEM INFORMACAO" (favorecido nao identificado pelo Portal).

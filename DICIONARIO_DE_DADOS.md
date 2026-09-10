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
- Cadastro do token (gratuito): https://portaldatransparencia.gov.br/api-de-dados/cadastrar-email
- Endpoint relevante: `/despesas/por-orgao` (parametros `codigoOrgao`, `mesAno`, `pagina`)
- Limitacoes: cota de requisicoes por minuto e paginacao; melhor para consultas pontuais
  do que para carga de periodo completo. Por isso o MVP usa os arquivos mensais.

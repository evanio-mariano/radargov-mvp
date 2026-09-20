# Modelo de dados - RadarGov (Sprint 2)

Duas tabelas fato, compartilhando as dimensoes de tempo e orgao/area. Nao
ha tabelas de dimensao separadas (SGBD dedicado seria excesso de engenharia
para o volume do MVP) - as dimensoes aparecem como colunas normalizadas
dentro de cada fato, o que e suficiente para os indicadores do MVP e para
o consumo direto pelo Power BI.

## Fato: despesas_tratada.parquet

Uma linha por combinacao **mes x area x orgao x funcao**.

| Coluna | Tipo | Dimensao | Descricao |
|---|---|---|---|
| ano_mes | texto (AAAA-MM) | tempo | mes de referencia |
| ano | inteiro | tempo | ano, derivado de ano_mes |
| mes | inteiro | tempo | mes (1-12), derivado de ano_mes |
| area | texto | area | saude / educacao / infraestrutura |
| orgao | texto | orgao | nome do orgao superior (Portal corta em 43 caracteres) |
| funcao | texto | - | funcao de governo (detalhe da despesa) |
| valor | numero | - | Valor Pago (R$), medida do fato |

Fonte: `dados/bruto/despesas_bruto.parquet` (coleta.py). Cobre as 3 areas
de interesse (saude, educacao, infraestrutura), 6 orgaos, janela de
MESES_JANELA meses.

## Fato: favorecidos_tratado.parquet

Uma linha por combinacao **mes x orgao x favorecido**, com o valor somado
entre as diferentes unidades gestoras do mesmo orgao (a base bruta,
`favorecidos_infraestrutura_bruto.parquet`, mantem o detalhe por unidade
gestora para auditoria).

| Coluna | Tipo | Dimensao | Descricao |
|---|---|---|---|
| ano_mes / ano / mes | - | tempo | mesmo padrao do fato de despesas |
| area | texto | area | sempre "infraestrutura" nesta versao do MVP |
| codigo_orgao | texto | orgao | codigo SIAFI do orgao superior |
| orgao | texto | orgao | nome do orgao superior |
| codigo_favorecido | texto | favorecido | CPF ou CNPJ |
| favorecido | texto | favorecido | nome do favorecido (ou "SEM INFORMACAO") |
| tipo_favorecido | texto | favorecido | classificacao do Portal (pessoa fisica, entidade privada, administracao publica, etc.) |
| valor | numero | - | valor recebido no mes, medida do fato |

Fonte: `dados/bruto/favorecidos_infraestrutura_bruto.parquet`
(coleta_favorecidos.py). Cobre apenas a area infraestrutura - ver
DICIONARIO_DE_DADOS.md para a justificativa da restricao de escopo.

## Como as duas tabelas se cruzam

As duas tabelas compartilham `ano_mes` (tempo), `area` e `orgao`
(mesmos nomes/codigos de orgao superior). Um indicador que precise
combinar "quanto o orgao gastou no total" (despesas_tratada) com "quem
recebeu" (favorecidos_tratado) pode ser feito com um `merge` por
`(ano_mes, orgao)` nas duas tabelas.

## Observacoes

- Valores negativos em favorecidos_tratado (615 linhas apos agregacao)
  representam estornos/devolucoes registrados pela fonte - nao sao
  removidos, para nao distorcer o total do periodo.
- "SEM INFORMACAO" como nome de favorecido e um valor legitimo da fonte
  (o Portal nao identifica o favorecido nesses casos), nao um erro do
  pipeline.

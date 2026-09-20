# Caderno de indicadores - RadarGov

Base: despesas_tratada.parquet | Periodo: 2026-03 a 2026-08

## 1. Execucao por area (total do periodo)

Formula: soma de `valor` (Valor Pago) agrupado por `area`, no periodo completo.

| Area | Valor (R$) |
|---|---|
| saude | 134,061,203,861.13 |
| educacao | 124,370,434,462.50 |
| infraestrutura | 61,892,687,437.34 |

## 2. Execucao por orgao (total do periodo)

Formula: soma de `valor` agrupado por `orgao`, no periodo completo.

| Area | Orgao | Valor (R$) |
|---|---|---|
| saude | Ministério da Saúde | 134,061,203,861.13 |
| educacao | Ministério da Educação | 124,370,434,462.50 |
| infraestrutura | Ministério das Cidades | 26,166,390,700.75 |
| infraestrutura | Ministério da Integração e do Desenvolvime | 18,762,964,752.94 |
| infraestrutura | Ministério de Portos e Aeroportos | 9,964,979,415.53 |
| infraestrutura | Ministério dos Transportes | 6,998,352,568.12 |

## 3. Serie historica mensal por area

Formula: soma de `valor` agrupado por `area` e `ano_mes`.

| Area | Mes | Valor (R$) |
|---|---|---|
| educacao | 2026-03 | 22,999,793,490.78 |
| educacao | 2026-04 | 18,938,734,012.92 |
| educacao | 2026-05 | 20,270,151,747.18 |
| educacao | 2026-06 | 19,659,526,331.48 |
| educacao | 2026-07 | 22,744,926,294.16 |
| educacao | 2026-08 | 19,757,302,585.98 |
| infraestrutura | 2026-03 | 8,857,188,319.88 |
| infraestrutura | 2026-04 | 4,386,553,125.98 |
| infraestrutura | 2026-05 | 8,774,554,437.07 |
| infraestrutura | 2026-06 | 9,510,167,312.30 |
| infraestrutura | 2026-07 | 16,335,831,891.80 |
| infraestrutura | 2026-08 | 14,028,392,350.31 |
| saude | 2026-03 | 16,795,027,177.83 |
| saude | 2026-04 | 19,880,788,850.11 |
| saude | 2026-05 | 29,371,965,930.71 |
| saude | 2026-06 | 29,203,873,682.49 |
| saude | 2026-07 | 20,338,964,918.08 |
| saude | 2026-08 | 18,470,583,301.91 |

## 4. Variacao mensal por area

Formula: `(valor do mes / valor do mes anterior - 1) x 100`. O primeiro mes de cada area nao tem mes anterior na janela coletada, por isso fica sem variacao calculada.

Exemplo: se educacao pagou R$ 20 mi em 2026-04 e R$ 22 mi em 2026-05, a variacao de maio e (22/20 - 1) x 100 = +10,0%.

| Area | Mes | Valor (R$) | Variacao vs mes anterior |
|---|---|---|---|
| educacao | 2026-03 | 22,999,793,490.78 | - |
| educacao | 2026-04 | 18,938,734,012.92 | -17.7% |
| educacao | 2026-05 | 20,270,151,747.18 | +7.0% |
| educacao | 2026-06 | 19,659,526,331.48 | -3.0% |
| educacao | 2026-07 | 22,744,926,294.16 | +15.7% |
| educacao | 2026-08 | 19,757,302,585.98 | -13.1% |
| infraestrutura | 2026-03 | 8,857,188,319.88 | - |
| infraestrutura | 2026-04 | 4,386,553,125.98 | -50.5% |
| infraestrutura | 2026-05 | 8,774,554,437.07 | +100.0% |
| infraestrutura | 2026-06 | 9,510,167,312.30 | +8.4% |
| infraestrutura | 2026-07 | 16,335,831,891.80 | +71.8% |
| infraestrutura | 2026-08 | 14,028,392,350.31 | -14.1% |
| saude | 2026-03 | 16,795,027,177.83 | - |
| saude | 2026-04 | 19,880,788,850.11 | +18.4% |
| saude | 2026-05 | 29,371,965,930.71 | +47.7% |
| saude | 2026-06 | 29,203,873,682.49 | -0.6% |
| saude | 2026-07 | 20,338,964,918.08 | -30.4% |
| saude | 2026-08 | 18,470,583,301.91 | -9.2% |

## 5. Ranking de favorecidos

Calculado separadamente, ver `ranking_favorecidos_infraestrutura.md` (escopo: area infraestrutura, ver DICIONARIO_DE_DADOS.md para a justificativa).
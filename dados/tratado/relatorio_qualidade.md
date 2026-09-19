# Relatorio de qualidade da base bruta - RadarGov

Gerado em: 19/09/2026 10:05
Arquivo analisado: `despesas_bruto.parquet`

## Visao geral

- Linhas: **434**
- Orgaos distintos: **6**
- Meses cobertos: **6** (2026-03 a 2026-08)
- Valor total executado: **R$ 320,324,325,760.97**

## Validacao de schema (Pandera)

- Resultado: **APROVADO**

## Completude (valores ausentes por coluna)

| coluna | nulos | % |
|---|---|---|
| ano_mes | 0 | 0.0% |
| area | 0 | 0.0% |
| orgao | 0 | 0.0% |
| funcao | 0 | 0.0% |
| valor | 0 | 0.0% |

## Outras checagens

- Linhas duplicadas: **0**
- Valores negativos: **0**
- Valores iguais a zero: **84**

## Valor executado por area

| area | valor (R$) |
|---|---|
| educacao | 124,370,434,462.50 |
| infraestrutura | 61,892,687,437.34 |
| saude | 134,061,203,861.13 |

## Cobertura por mes

| mes | linhas | valor (R$) |
|---|---|---|
| 2026-03 | 71 | 48,652,008,988.49 |
| 2026-04 | 70 | 43,206,075,989.01 |
| 2026-05 | 74 | 58,416,672,114.96 |
| 2026-06 | 73 | 58,373,567,326.27 |
| 2026-07 | 74 | 59,419,723,104.04 |
| 2026-08 | 72 | 52,256,278,238.20 |
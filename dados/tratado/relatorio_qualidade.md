# Relatorio de qualidade da base bruta - RadarGov

Gerado em: 01/10/2026 12:12
Arquivo analisado: `despesas_bruto.parquet`

## Visao geral

- Linhas: **437**
- Orgaos distintos: **6**
- Meses cobertos: **6** (2026-04 a 2026-09)
- Valor total executado: **R$ 316,884,562,219.37**

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
- Valores iguais a zero: **69**

## Valor executado por area

| area | valor (R$) |
|---|---|
| educacao | 117,443,442,871.15 |
| infraestrutura | 61,203,720,951.66 |
| saude | 138,237,398,396.56 |

## Cobertura por mes

| mes | linhas | valor (R$) |
|---|---|---|
| 2026-04 | 70 | 43,206,075,989.01 |
| 2026-05 | 74 | 58,416,672,114.96 |
| 2026-06 | 73 | 58,373,567,326.27 |
| 2026-07 | 74 | 59,419,723,104.04 |
| 2026-08 | 72 | 52,256,278,238.20 |
| 2026-09 | 74 | 45,212,245,446.89 |
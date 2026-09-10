# -*- coding: utf-8 -*-
"""
QUALIDADE - RadarGov

Le a base bruta gerada pela coleta e produz:
  - uma validacao de schema com Pandera (tipos e regras de negocio);
  - um relatorio de qualidade em dados/tratado/relatorio_qualidade.md
    (nulos, duplicidades, cobertura de meses, faixa de valores).

Como rodar:  python src/qualidade.py   (depois de rodar coleta.py)
"""
import sys
import datetime as dt
from pathlib import Path

import pandas as pd
import pandera.pandas as pa
from pandera.pandas import Column, Check
from pandera.errors import SchemaErrors

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config as cfg


schema = pa.DataFrameSchema(
    {
        "ano_mes": Column(str, Check.str_matches(r"^\d{4}-\d{2}$")),
        "area":    Column(str, Check.isin(cfg.AREAS)),
        "orgao":   Column(str, Check.str_length(min_value=1)),
        "funcao":  Column(str, nullable=True),
        "valor":   Column(float, Check.ge(0), nullable=True),
    },
    strict=True,
    coerce=True,
)


def main() -> int:
    if not cfg.ARQ_BASE_BRUTA.exists():
        print(f"Base bruta nao encontrada: {cfg.ARQ_BASE_BRUTA}")
        print("Rode antes:  python src/coleta.py")
        return 1

    df = pd.read_parquet(cfg.ARQ_BASE_BRUTA)
    cfg.DIR_TRATADO.mkdir(parents=True, exist_ok=True)

    # ---- validacao de schema ----
    erros_schema = []
    try:
        schema.validate(df, lazy=True)
        schema_ok = True
    except SchemaErrors as e:
        schema_ok = False
        erros_schema = e.failure_cases.to_dict("records")

    # ---- checagens de qualidade ----
    nulos = df.isna().sum()
    duplicadas = int(df.duplicated().sum())
    meses = sorted(df["ano_mes"].unique())
    valores_negativos = int((df["valor"] < 0).sum())
    valor_zero = int((df["valor"] == 0).sum())

    linhas = []
    linhas.append("# Relatorio de qualidade da base bruta - RadarGov")
    linhas.append("")
    linhas.append(f"Gerado em: {dt.datetime.now():%d/%m/%Y %H:%M}")
    linhas.append(f"Arquivo analisado: `{cfg.ARQ_BASE_BRUTA.name}`")
    linhas.append("")
    linhas.append("## Visao geral")
    linhas.append("")
    linhas.append(f"- Linhas: **{len(df):,}**")
    linhas.append(f"- Orgaos distintos: **{df['orgao'].nunique()}**")
    linhas.append(f"- Meses cobertos: **{len(meses)}** ({meses[0]} a {meses[-1]})")
    linhas.append(f"- Valor total executado: **R$ {df['valor'].sum():,.2f}**")
    linhas.append("")
    linhas.append("## Validacao de schema (Pandera)")
    linhas.append("")
    linhas.append(f"- Resultado: **{'APROVADO' if schema_ok else 'REPROVADO'}**")
    if not schema_ok:
        linhas.append(f"- Ocorrencias: {len(erros_schema)} (primeiras 20 abaixo)")
        linhas.append("")
        linhas.append("| coluna | verificacao | valor |")
        linhas.append("|---|---|---|")
        for e in erros_schema[:20]:
            linhas.append(f"| {e.get('column')} | {e.get('check')} | {e.get('failure_case')} |")
    linhas.append("")
    linhas.append("## Completude (valores ausentes por coluna)")
    linhas.append("")
    linhas.append("| coluna | nulos | % |")
    linhas.append("|---|---|---|")
    for col, n in nulos.items():
        linhas.append(f"| {col} | {int(n)} | {n/len(df)*100:.1f}% |")
    linhas.append("")
    linhas.append("## Outras checagens")
    linhas.append("")
    linhas.append(f"- Linhas duplicadas: **{duplicadas}**")
    linhas.append(f"- Valores negativos: **{valores_negativos}**")
    linhas.append(f"- Valores iguais a zero: **{valor_zero}**")
    linhas.append("")
    linhas.append("## Valor executado por area")
    linhas.append("")
    linhas.append("| area | valor (R$) |")
    linhas.append("|---|---|")
    for area, v in df.groupby("area")["valor"].sum().items():
        linhas.append(f"| {area} | {v:,.2f} |")
    linhas.append("")
    linhas.append("## Cobertura por mes")
    linhas.append("")
    linhas.append("| mes | linhas | valor (R$) |")
    linhas.append("|---|---|---|")
    for (mes), g in df.groupby("ano_mes"):
        linhas.append(f"| {mes} | {len(g)} | {g['valor'].sum():,.2f} |")

    cfg.ARQ_RELATORIO.write_text("\n".join(linhas), encoding="utf-8")

    print("Relatorio gerado:", cfg.ARQ_RELATORIO)
    print("Schema:", "APROVADO" if schema_ok else f"REPROVADO ({len(erros_schema)} ocorrencias)")
    print(f"Duplicadas: {duplicadas} | Nulos em 'orgao': {int(nulos.get('orgao', 0))}")
    return 0 if schema_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

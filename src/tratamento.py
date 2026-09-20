# -*- coding: utf-8 -*-
"""
TRATAMENTO - RadarGov (Sprint 2)

Le as bases brutas (despesas por orgao/area e favorecidos de
infraestrutura) e produz as bases tratadas, prontas para calculo de
indicadores: tipos padronizados, dimensao de tempo explicita, e o fato
de favorecidos agregado por (mes, orgao, favorecido) - a granularidade
por unidade gestora da base bruta so importa para auditoria, nao para
os indicadores do MVP.

Modelo de dados (dimensoes de orgao, area, favorecido e tempo):
  - despesas_tratada.parquet   : fato de despesas (mes x area x orgao x funcao)
  - favorecidos_tratado.parquet: fato de favorecidos (mes x orgao x favorecido)
  Ambas as tabelas compartilham a coluna "ano_mes" (dimensao tempo) e
  "orgao"/"area" (dimensao orgao), permitindo cruzamento.

Como rodar:  python src/tratamento.py   (depois de coleta.py e coleta_favorecidos.py)
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config as cfg


def tratar_despesas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["orgao"] = df["orgao"].str.strip()
    df["funcao"] = df["funcao"].str.strip()
    df["valor"] = df["valor"].round(2)
    df["ano"] = df["ano_mes"].str[:4].astype(int)
    df["mes"] = df["ano_mes"].str[5:7].astype(int)
    df = df.sort_values(["ano_mes", "area", "orgao", "funcao"]).reset_index(drop=True)
    return df[["ano_mes", "ano", "mes", "area", "orgao", "funcao", "valor"]]


def tratar_favorecidos(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ano_mes"] = df["anoMes"].astype(str).str.slice(0, 4) + "-" + df["anoMes"].astype(str).str.slice(4, 6)
    df["ano"] = df["ano_mes"].str[:4].astype(int)
    df["mes"] = df["ano_mes"].str[5:7].astype(int)
    df["nomePessoa"] = df["nomePessoa"].str.strip()
    df["area"] = cfg.FAV_AREA

    # agrega por mes x orgao superior x favorecido, somando entre unidades
    # gestoras (a base bruta guarda o detalhe por UG, para auditoria)
    tratado = (
        df.groupby(
            ["ano_mes", "ano", "mes", "area", "codigoOrgaoSuperior", "nomeOrgaoSuperior",
             "codigoPessoa", "nomePessoa", "tipoPessoa"],
            as_index=False,
        )["valor"].sum()
    )
    tratado = tratado.rename(columns={
        "codigoOrgaoSuperior": "codigo_orgao",
        "nomeOrgaoSuperior": "orgao",
        "codigoPessoa": "codigo_favorecido",
        "nomePessoa": "favorecido",
        "tipoPessoa": "tipo_favorecido",
    })
    tratado["valor"] = tratado["valor"].round(2)
    tratado = tratado.sort_values(["ano_mes", "orgao", "valor"], ascending=[True, True, False]).reset_index(drop=True)
    cols = ["ano_mes", "ano", "mes", "area", "codigo_orgao", "orgao",
            "codigo_favorecido", "favorecido", "tipo_favorecido", "valor"]
    return tratado[cols]


def main() -> int:
    if not cfg.ARQ_BASE_BRUTA.exists():
        print(f"Base bruta de despesas nao encontrada: {cfg.ARQ_BASE_BRUTA}")
        print("Rode antes: python src/coleta.py")
        return 1
    if not cfg.ARQ_FAV_INFRA_BRUTO.exists():
        print(f"Base bruta de favorecidos nao encontrada: {cfg.ARQ_FAV_INFRA_BRUTO}")
        print("Rode antes: python src/coleta_favorecidos.py")
        return 1

    despesas = pd.read_parquet(cfg.ARQ_BASE_BRUTA)
    favorecidos = pd.read_parquet(cfg.ARQ_FAV_INFRA_BRUTO)

    despesas_tratada = tratar_despesas(despesas)
    favorecidos_tratado = tratar_favorecidos(favorecidos)

    cfg.DIR_TRATADO.mkdir(parents=True, exist_ok=True)
    despesas_tratada.to_parquet(cfg.ARQ_DESPESAS_TRATADA, index=False)
    favorecidos_tratado.to_parquet(cfg.ARQ_FAV_TRATADO, index=False)

    negativos = int((favorecidos_tratado["valor"] < 0).sum())

    print("=== despesas_tratada ===")
    print(f"  linhas: {len(despesas_tratada)} | periodo: {despesas_tratada['ano_mes'].min()} a {despesas_tratada['ano_mes'].max()}")
    print(f"  salvo em: {cfg.ARQ_DESPESAS_TRATADA}")
    print()
    print("=== favorecidos_tratado ===")
    print(f"  linhas: {len(favorecidos_tratado)} | favorecidos distintos: {favorecidos_tratado['codigo_favorecido'].nunique()}")
    print(f"  valores negativos (estornos/devolucoes): {negativos}")
    print(f"  salvo em: {cfg.ARQ_FAV_TRATADO}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

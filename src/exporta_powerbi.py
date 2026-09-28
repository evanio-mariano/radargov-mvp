# -*- coding: utf-8 -*-
"""
EXPORTACAO PARA O POWER BI - RadarGov (Sprint 3)

Le as bases tratadas (Parquet) e grava, em dados/tratado/powerbi/, um
conjunto de arquivos CSV prontos para o dashboard:

  despesas.csv     fato de despesas (mes x area x orgao x funcao)
  favorecidos.csv  fato de favorecidos (mes x orgao x favorecido, infraestrutura)
  sinalizacao.csv  serie mensal por orgao com variacao e marca de atipico
  dim_orgao.csv    dimensao de orgao (codigo, nome completo, area)
  dim_tempo.csv    dimensao de tempo (mes de referencia)
  metadados.csv    data/hora da ultima atualizacao e periodo coberto

Por que CSV: o Power BI le CSV publicado no GitHub (link direto, sem
login) e consegue atualizar o relatorio a partir dele. Codificacao
UTF-8 (sem BOM), separador virgula, ponto como separador decimal.

Como rodar:  python src/exporta_powerbi.py   (depois de sinalizacao.py)
"""
import sys
import datetime as dt
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config as cfg

MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def gravar(df: pd.DataFrame, nome: str) -> Path:
    caminho = cfg.DIR_POWERBI / nome
    df.to_csv(caminho, index=False, encoding="utf-8")
    return caminho


def main() -> int:
    faltando = [p for p in (cfg.ARQ_DESPESAS_TRATADA, cfg.ARQ_FAV_TRATADO, cfg.ARQ_DESPESAS_SINALIZADA)
                if not p.exists()]
    if faltando:
        print("Arquivos faltando, rode antes tratamento.py e sinalizacao.py:")
        for p in faltando:
            print(f"  {p}")
        return 1

    cfg.DIR_POWERBI.mkdir(parents=True, exist_ok=True)

    despesas = pd.read_parquet(cfg.ARQ_DESPESAS_TRATADA)
    favorecidos = pd.read_parquet(cfg.ARQ_FAV_TRATADO)
    sinal = pd.read_parquet(cfg.ARQ_DESPESAS_SINALIZADA)

    # sinalizacao: marca legivel + marca numerica (facilita somar no Power BI)
    sinal = sinal.copy()
    sinal["atipico_flag"] = sinal["atipico"].astype(int)
    sinal["atipico"] = sinal["atipico"].map({True: "Sim", False: "Nao"})

    # dimensao de orgao (uma linha por orgao presente nas duas bases)
    dim_orgao = (
        pd.concat([
            despesas[["codigo_orgao", "orgao", "area"]],
            favorecidos[["codigo_orgao", "orgao", "area"]],
        ])
        .drop_duplicates(subset=["codigo_orgao"])
        .sort_values(["area", "orgao"])
        .reset_index(drop=True)
    )

    # dimensao de tempo
    meses = sorted(set(despesas["ano_mes"]) | set(favorecidos["ano_mes"]))
    dim_tempo = pd.DataFrame({"ano_mes": meses})
    dim_tempo["data"] = pd.to_datetime(dim_tempo["ano_mes"] + "-01").dt.strftime("%Y-%m-%d")
    dim_tempo["ano"] = dim_tempo["ano_mes"].str[:4].astype(int)
    dim_tempo["mes"] = dim_tempo["ano_mes"].str[5:7].astype(int)
    dim_tempo["indice_mes"] = range(1, len(dim_tempo) + 1)   # 1 = mes mais antigo
    dim_tempo["mes_rotulo"] = dim_tempo.apply(lambda r: f"{MESES[r['mes'] - 1]}/{r['ano']}", axis=1)

    # metadados (data da ultima atualizacao, horario de Brasilia)
    agora = dt.datetime.now(ZoneInfo("America/Sao_Paulo"))
    metadados = pd.DataFrame([{
        "atualizado_em": agora.strftime("%Y-%m-%d %H:%M:%S"),
        "atualizado_em_texto": agora.strftime("%d/%m/%Y %H:%M"),
        "periodo_inicio": meses[0],
        "periodo_fim": meses[-1],
        "linhas_despesas": len(despesas),
        "linhas_favorecidos": len(favorecidos),
        "fonte": "Portal da Transparencia do Governo Federal",
    }])

    saidas = {
        "despesas.csv": despesas,
        "favorecidos.csv": favorecidos,
        "sinalizacao.csv": sinal,
        "dim_orgao.csv": dim_orgao,
        "dim_tempo.csv": dim_tempo,
        "metadados.csv": metadados,
    }
    for nome, df in saidas.items():
        caminho = gravar(df, nome)
        print(f"  {nome:18} {len(df):>7} linhas  ({caminho.stat().st_size / 1024:,.0f} KB)")

    print(f"\nArquivos gravados em: {cfg.DIR_POWERBI}")
    print(f"Ultima atualizacao registrada: {metadados.iloc[0]['atualizado_em_texto']} (Brasilia)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

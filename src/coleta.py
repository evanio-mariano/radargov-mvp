# -*- coding: utf-8 -*-
"""
COLETA - RadarGov

O que este script faz:
  1. Descobre os meses da janela (config.MESES_JANELA).
  2. Para cada mes: baixa o arquivo "Execucao da Despesa" do Portal da
     Transparencia (ou usa um arquivo ja colocado em dados/entrada/).
  3. Le o CSV, mantem so as colunas de interesse, classifica cada despesa
     em uma area (saude / educacao / infraestrutura) pela tabela de-para.
  4. Junta tudo e grava a base bruta em dados/bruto/despesas_bruto.parquet.
  5. Imprime um resumo (meses processados, linhas, periodo, valor total).

Como rodar:  python src/coleta.py
"""
import sys
import io
import zipfile
import datetime as dt
from pathlib import Path

import requests
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config as cfg


def meses_da_janela(qtd: int) -> list[str]:
    """Retorna uma lista de 'AAAAMM', do mais antigo ao mais recente,
    terminando no mes anterior ao atual."""
    hoje = dt.date.today().replace(day=1)
    fim = hoje - dt.timedelta(days=1)          # ultimo dia do mes passado
    fim = fim.replace(day=1)
    meses = []
    ref = fim
    for _ in range(qtd):
        meses.append(ref.strftime("%Y%m"))
        # volta um mes
        ref = (ref - dt.timedelta(days=1)).replace(day=1)
    return sorted(meses)


def baixar_ou_localizar(aaaamm: str) -> Path | None:
    """Devolve o caminho de um ZIP/CSV para o mes. Primeiro procura em
    dados/entrada/; se nao achar, tenta baixar do Portal."""
    # 1) arquivo ja presente?
    for padrao in (f"*{aaaamm}*.zip", f"*{aaaamm}*.csv", f"*{aaaamm}*.CSV"):
        achados = list(cfg.DIR_ENTRADA.glob(padrao))
        if achados:
            print(f"  [{aaaamm}] usando arquivo local: {achados[0].name}")
            return achados[0]

    # 2) tentar download
    url = cfg.URL_DOWNLOAD.format(aaaamm=aaaamm)
    destino = cfg.DIR_ENTRADA / f"{aaaamm}_despesas.zip"
    try:
        print(f"  [{aaaamm}] baixando: {url}")
        r = requests.get(url, timeout=180, headers={"User-Agent": "RadarGov-MVP/1.0"})
        r.raise_for_status()
        destino.write_bytes(r.content)
        print(f"  [{aaaamm}] baixado ({len(r.content)/1_000_000:.1f} MB)")
        return destino
    except Exception as e:
        print(f"  [{aaaamm}] FALHA no download ({e}).")
        print(f"           Baixe manualmente em "
              f"https://portaldatransparencia.gov.br/download-de-dados/despesas-execucao")
        print(f"           e salve o arquivo em: {cfg.DIR_ENTRADA}")
        return None


def ler_csv(caminho: Path) -> pd.DataFrame:
    """Le o CSV (dentro de um ZIP ou solto)."""
    if caminho.suffix.lower() == ".zip":
        with zipfile.ZipFile(caminho) as z:
            nome_csv = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
            with z.open(nome_csv) as f:
                dados = f.read()
        buffer = io.BytesIO(dados)
    else:
        buffer = caminho

    return pd.read_csv(
        buffer,
        sep=cfg.CSV_SEP,
        encoding=cfg.CSV_ENCODING,
        decimal=cfg.CSV_DECIMAL,
        dtype=str,               # le tudo como texto; convertemos o valor depois
        low_memory=False,
    )


def para_numero(serie: pd.Series) -> pd.Series:
    """'1.234.567,89' -> 1234567.89"""
    return (
        serie.astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .replace({"": None, "nan": None})
        .astype(float)
    )


def main() -> int:
    cfg.DIR_ENTRADA.mkdir(parents=True, exist_ok=True)
    cfg.DIR_BRUTO.mkdir(parents=True, exist_ok=True)

    de_para = pd.read_csv(cfg.ARQ_DE_PARA, sep=";", dtype=str)
    de_para["codigo_orgao"] = de_para["codigo_orgao"].str.strip()
    mapa = dict(zip(de_para["codigo_orgao"], de_para["area"]))
    print(f"Tabela de-para: {len(mapa)} orgaos mapeados em {de_para['area'].nunique()} areas.\n")

    meses = meses_da_janela(cfg.MESES_JANELA)
    print(f"Janela: {meses[0]} a {meses[-1]}  ({len(meses)} meses)\n")

    partes = []
    nao_mapeados = []          # orgaos que apareceram mas nao estao na de-para
    colunas_conferidas = False
    for aaaamm in meses:
        arq = baixar_ou_localizar(aaaamm)
        if arq is None:
            continue
        try:
            df = ler_csv(arq)
        except Exception as e:
            print(f"  [{aaaamm}] erro ao ler o CSV: {e}")
            continue

        if not colunas_conferidas:
            print("\n--- COLUNAS ENCONTRADAS NO ARQUIVO ---")
            for c in df.columns:
                print(f"   {c!r}")
            print("--- ajuste COL_ORGAO / COL_FUNCAO / COL_VALOR em config.py se os nomes acima nao baterem ---\n")
            colunas_conferidas = True

        faltando = [c for c in (cfg.COL_COD_ORGAO, cfg.COL_ORGAO, cfg.COL_FUNCAO, cfg.COL_VALOR) if c not in df.columns]
        if faltando:
            print(f"  [{aaaamm}] PULADO: colunas nao encontradas: {faltando}")
            print(f"           Edite config.py com os nomes exatos listados acima.")
            continue

        sub = df[[cfg.COL_COD_ORGAO, cfg.COL_ORGAO, cfg.COL_FUNCAO, cfg.COL_VALOR]].copy()
        sub.columns = ["cod_orgao", "orgao", "funcao", "valor"]
        sub["cod_orgao"] = sub["cod_orgao"].str.strip()
        sub["orgao"] = sub["orgao"].str.strip()
        sub["ano_mes"] = f"{aaaamm[:4]}-{aaaamm[4:]}"
        sub["valor"] = para_numero(sub["valor"])
        sub["area"] = sub["cod_orgao"].map(mapa)

        # guarda os orgaos sem classificacao, com o valor do mes, para diagnostico
        fora = sub[sub["area"].isna()]
        if not fora.empty:
            nao_mapeados.append(fora.groupby(["cod_orgao", "orgao"], as_index=False)["valor"].sum())

        sub = sub[sub["area"].isin(cfg.AREAS)]           # so as areas de interesse
        sub = sub.groupby(["ano_mes", "area", "orgao", "funcao"], as_index=False)["valor"].sum()
        partes.append(sub)
        print(f"  [{aaaamm}] OK  {len(sub):>6} linhas  R$ {sub['valor'].sum():,.0f}")

    if nao_mapeados:
        diag = (
            pd.concat(nao_mapeados, ignore_index=True)
            .groupby(["cod_orgao", "orgao"], as_index=False)["valor"].sum()
            .sort_values("valor", ascending=False)
        )
        print("\n--- ORGAOS AINDA SEM CLASSIFICACAO (top 25 por valor) ---")
        print("    Copie para de_para_orgao_area.csv os que forem de saude,")
        print("    educacao ou infraestrutura (linha:  codigo;nome;area)\n")
        for _, r in diag.head(25).iterrows():
            print(f"   {r['cod_orgao']:>7}   R$ {r['valor']:>18,.2f}   {r['orgao']}")
        print("--------------------------------------------------------\n")

    if not partes:
        print("\nNENHUM mes foi processado (nenhum orgao da de-para bateu com o arquivo).")
        print("Use a lista acima para preencher de_para_orgao_area.csv e rode de novo.")
        return 1

    base = pd.concat(partes, ignore_index=True).sort_values(["ano_mes", "area", "orgao"])
    base.to_parquet(cfg.ARQ_BASE_BRUTA, index=False)

    print("\n================ RESUMO ================")
    print(f"Arquivo gerado : {cfg.ARQ_BASE_BRUTA}")
    print(f"Linhas         : {len(base):,}")
    print(f"Periodo        : {base['ano_mes'].min()} a {base['ano_mes'].max()}")
    print(f"Meses cobertos : {base['ano_mes'].nunique()} de {len(meses)}")
    print(f"Orgaos         : {base['orgao'].nunique()}")
    print(f"Valor total    : R$ {base['valor'].sum():,.2f}")
    print("Por area:")
    for area, v in base.groupby("area")["valor"].sum().items():
        print(f"   {area:15} R$ {v:,.2f}")
    print("=======================================")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

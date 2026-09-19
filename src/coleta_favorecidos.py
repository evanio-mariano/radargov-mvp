# -*- coding: utf-8 -*-
"""
COLETA FAVORECIDOS - RadarGov (producao)

Coleta os recebimentos de recursos por favorecido para todos os orgaos
de uma area (config.FAV_AREA, padrao "infraestrutura"), na mesma janela
de meses do pipeline principal (config.MESES_JANELA), e monta o ranking
dos maiores favorecidos do periodo.

Diferente de coleta.py:
  - Consulta a API do Portal (endpoint paginado), nao um arquivo unico
    por mes - a API nao permite pedir os maiores valores primeiro, entao
    e preciso percorrer todas as paginas de cada orgao/mes.
  - Precisa de uma chave de API (arquivo .env, variavel PORTAL_API_KEY).
  - So cobre a area configurada. Saude e educacao foram medidas na
    Sprint 2 e tem volume mensal grande demais para o MVP (ver
    DICIONARIO_DE_DADOS.md) - ficam fora deste script de proposito.

Como rodar:  python src/coleta_favorecidos.py
Tempo esperado: dezenas de minutos, proporcional ao numero de orgaos x
meses x paginas por combinacao (infraestrutura: ~600-650 paginas/mes).
"""
import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # para "import config"
sys.path.insert(0, str(Path(__file__).resolve().parent))          # para "from coleta import ..."
import config as cfg
from coleta import meses_da_janela

URL = "https://api.portaldatransparencia.gov.br/api-de-dados/despesas/recursos-recebidos"
PAUSA_ENTRE_CHAMADAS = 0.35  # segundos; ~170 chamadas/min, bem abaixo do limite de 400/min


def aaaamm_para_mmaaaa(aaaamm: str) -> str:
    """'202603' -> '03/2026'"""
    return f"{aaaamm[4:]}/{aaaamm[:4]}"


def coletar_orgao_mes(headers: dict, cod_orgao: str, nome_orgao: str, mes_mmaaaa: str) -> list:
    """Percorre todas as paginas de um (orgao, mes) ate a API sinalizar o fim."""
    registros = []
    pagina = 1
    completou = False
    while pagina <= cfg.FAV_MAX_PAGINAS_POR_COMBO:
        params = {
            "mesAnoInicio": mes_mmaaaa,
            "mesAnoFim": mes_mmaaaa,
            "orgaoSuperior": cod_orgao,
            "pagina": pagina,
        }
        try:
            r = requests.get(URL, headers=headers, params=params, timeout=60)
        except Exception as e:
            print(f"    [pagina {pagina}] erro de conexao: {e}")
            break

        if r.status_code == 401:
            raise RuntimeError("Chave de API invalida ou nao autorizada (401). Confira o .env.")
        if r.status_code == 429:
            print("    limite de requisicoes atingido, aguardando 30s...")
            time.sleep(30)
            continue
        if r.status_code != 200:
            print(f"    [pagina {pagina}] erro HTTP {r.status_code}: {r.text[:150]}")
            break

        dados = r.json()
        if not dados:
            completou = True
            break

        registros.extend(dados)
        pagina += 1
        time.sleep(PAUSA_ENTRE_CHAMADAS)

    if not completou and pagina > cfg.FAV_MAX_PAGINAS_POR_COMBO:
        print(f"    AVISO: {nome_orgao} / {mes_mmaaaa} atingiu o limite de "
              f"{cfg.FAV_MAX_PAGINAS_POR_COMBO} paginas sem a API sinalizar o fim. "
              f"Dados deste orgao/mes podem estar incompletos.")

    return registros


def main() -> int:
    load_dotenv(cfg.RAIZ / ".env")
    chave = os.environ.get("PORTAL_API_KEY")
    if not chave:
        print("PORTAL_API_KEY nao encontrada.")
        print(f"Crie um arquivo .env em {cfg.RAIZ} com a linha:")
        print("  PORTAL_API_KEY=sua_chave_aqui")
        print("(copie .env.example e preencha)")
        return 1
    headers = {"chave-api-dados": chave, "accept": "application/json"}

    de_para = pd.read_csv(cfg.ARQ_DE_PARA, sep=";", dtype=str)
    orgaos = list(
        de_para.loc[de_para["area"] == cfg.FAV_AREA, ["codigo_orgao", "nome_orgao"]]
        .drop_duplicates()
        .itertuples(index=False, name=None)
    )
    if not orgaos:
        print(f"Nenhum orgao encontrado para a area '{cfg.FAV_AREA}' em {cfg.ARQ_DE_PARA}.")
        return 1

    meses = [aaaamm_para_mmaaaa(m) for m in meses_da_janela(cfg.MESES_JANELA)]
    print(f"Area: {cfg.FAV_AREA}")
    print(f"Orgaos ({len(orgaos)}): {', '.join(nome for _, nome in orgaos)}")
    print(f"Meses ({len(meses)}): {meses[0]} a {meses[-1]}\n")

    todos = []
    for cod_orgao, nome_orgao in orgaos:
        for mes in meses:
            print(f"  {nome_orgao} ({cod_orgao}) - {mes}...")
            regs = coletar_orgao_mes(headers, cod_orgao, nome_orgao, mes)
            print(f"    {len(regs)} registros")
            todos.extend(regs)

    if not todos:
        print("\nNenhum registro coletado. Verifique a chave e a tabela de-para.")
        return 1

    df = pd.DataFrame(todos)
    cfg.DIR_BRUTO.mkdir(parents=True, exist_ok=True)
    cfg.DIR_TRATADO.mkdir(parents=True, exist_ok=True)
    df.to_parquet(cfg.ARQ_FAV_INFRA_BRUTO, index=False)

    ranking = (
        df.groupby(["codigoPessoa", "nomePessoa"], as_index=False)["valor"]
        .sum()
        .sort_values("valor", ascending=False)
        .head(20)
    )

    linhas = []
    linhas.append(f"# Ranking de favorecidos - area {cfg.FAV_AREA} - RadarGov")
    linhas.append("")
    linhas.append(f"Orgaos: {', '.join(nome for _, nome in orgaos)}")
    linhas.append(f"Periodo: {meses[0]} a {meses[-1]} ({len(meses)} meses)")
    linhas.append(f"Registros brutos: {len(df)} | Favorecidos distintos: {df['codigoPessoa'].nunique()}")
    linhas.append("")
    linhas.append("## Top 20 favorecidos por valor recebido no periodo")
    linhas.append("")
    linhas.append("| Favorecido | Codigo (CPF/CNPJ) | Valor recebido (R$) |")
    linhas.append("|---|---|---|")
    for _, row in ranking.iterrows():
        linhas.append(f"| {row['nomePessoa']} | {row['codigoPessoa']} | {row['valor']:,.2f} |")

    cfg.ARQ_FAV_INFRA_RANKING.write_text("\n".join(linhas), encoding="utf-8")

    print(f"\nBase bruta salva em : {cfg.ARQ_FAV_INFRA_BRUTO}")
    print(f"Ranking salvo em    : {cfg.ARQ_FAV_INFRA_RANKING}")
    print("\nTop 5 favorecidos do periodo:")
    for _, row in ranking.head(5).iterrows():
        print(f"  R$ {row['valor']:>18,.2f}  {row['nomePessoa']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# -*- coding: utf-8 -*-
"""
COLETA FAVORECIDOS (PILOTO) - RadarGov

Testa, em escopo restrito (1 orgao, 1 mes), se e viavel construir um
ranking de favorecidos usando a API do Portal da Transparencia.

Diferente do coleta.py (Sprint 1), este script:
  - Precisa de uma chave de API (arquivo .env, variavel PORTAL_API_KEY).
  - Percorre TODAS as paginas do periodo/orgao, porque a API nao permite
    pedir os maiores valores primeiro (nao tem parametro de ordenacao).
  - E um piloto isolado: se travar ou faltar chave, avisa e para, sem
    afetar o pipeline principal (coleta.py / qualidade.py).

Como rodar:  python src/coleta_favorecidos_piloto.py
"""
import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config as cfg

URL = "https://api.portaldatransparencia.gov.br/api-de-dados/despesas/recursos-recebidos"
PAUSA_ENTRE_CHAMADAS = 0.35  # segundos; ~170 chamadas/min, bem abaixo do limite de 400/min


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
    params_base = {
        "mesAnoInicio": cfg.FAV_MES_ANO,
        "mesAnoFim": cfg.FAV_MES_ANO,
        "orgaoSuperior": cfg.FAV_ORGAO_SUPERIOR,
    }

    print(f"Piloto: orgao superior {cfg.FAV_ORGAO_SUPERIOR}, mes {cfg.FAV_MES_ANO}")
    print(f"Limite de seguranca: {cfg.FAV_MAX_PAGINAS} paginas\n")

    registros = []
    pagina = 1
    completou_naturalmente = False
    while pagina <= cfg.FAV_MAX_PAGINAS:
        params = dict(params_base, pagina=pagina)
        try:
            r = requests.get(URL, headers=headers, params=params, timeout=60)
        except Exception as e:
            print(f"  [pagina {pagina}] erro de conexao: {e}")
            break

        if r.status_code == 401:
            print("  ERRO 401: chave de API invalida ou nao autorizada.")
            print("  Confira o valor em .env (PORTAL_API_KEY).")
            return 1
        if r.status_code == 429:
            print(f"  [pagina {pagina}] limite de requisicoes atingido, aguardando 30s...")
            time.sleep(30)
            continue
        if r.status_code != 200:
            print(f"  [pagina {pagina}] erro HTTP {r.status_code}: {r.text[:200]}")
            break

        dados = r.json()
        if not dados:
            print(f"  [pagina {pagina}] vazia -> fim dos resultados.")
            completou_naturalmente = True
            break

        registros.extend(dados)
        if pagina == 1 or pagina % 10 == 0:
            print(f"  [pagina {pagina}] {len(dados)} registros nesta pagina, {len(registros)} acumulados")

        pagina += 1
        time.sleep(PAUSA_ENTRE_CHAMADAS)

    if not completou_naturalmente and pagina > cfg.FAV_MAX_PAGINAS:
        print(f"\nAVISO: atingiu o limite de seguranca de {cfg.FAV_MAX_PAGINAS} paginas")
        print("sem a API sinalizar o fim dos resultados. O ranking abaixo pode estar incompleto.")

    if not registros:
        print("\nNenhum registro coletado. Verifique a chave, o orgao e o mes configurados.")
        return 1

    df = pd.DataFrame(registros)
    cfg.DIR_BRUTO.mkdir(parents=True, exist_ok=True)
    cfg.DIR_TRATADO.mkdir(parents=True, exist_ok=True)
    df.to_parquet(cfg.ARQ_FAV_BRUTO, index=False)

    # ranking: soma o valor por favorecido (pode aparecer em mais de uma
    # unidade gestora / pagina dentro do mesmo orgao e mes)
    ranking = (
        df.groupby(["codigoPessoa", "nomePessoa"], as_index=False)["valor"]
        .sum()
        .sort_values("valor", ascending=False)
        .head(20)
    )

    linhas = []
    linhas.append("# Ranking de favorecidos (PILOTO) - RadarGov")
    linhas.append("")
    linhas.append(f"Orgao superior: {cfg.FAV_ORGAO_SUPERIOR} | Mes: {cfg.FAV_MES_ANO}")
    linhas.append(f"Paginas percorridas: {pagina - 1} | Registros brutos: {len(df)}")
    linhas.append(f"Favorecidos distintos: {df['codigoPessoa'].nunique()}")
    linhas.append(f"Coleta completa (API sinalizou fim): {'sim' if completou_naturalmente else 'NAO - ver aviso acima'}")
    linhas.append("")
    linhas.append("## Top 20 favorecidos por valor recebido")
    linhas.append("")
    linhas.append("| Favorecido | Codigo (CPF/CNPJ) | Valor recebido (R$) |")
    linhas.append("|---|---|---|")
    for _, row in ranking.iterrows():
        linhas.append(f"| {row['nomePessoa']} | {row['codigoPessoa']} | {row['valor']:,.2f} |")

    cfg.ARQ_FAV_RANKING.write_text("\n".join(linhas), encoding="utf-8")

    print(f"\nBase bruta salva em : {cfg.ARQ_FAV_BRUTO}")
    print(f"Ranking salvo em    : {cfg.ARQ_FAV_RANKING}")
    print("\nTop 5 favorecidos:")
    for _, row in ranking.head(5).iterrows():
        print(f"  R$ {row['valor']:>18,.2f}  {row['nomePessoa']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

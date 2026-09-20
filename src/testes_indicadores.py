# -*- coding: utf-8 -*-
"""
TESTES DOS INDICADORES - RadarGov (Sprint 2)

Suite de testes automatizados simples (asserts + relatorio PASS/FAIL),
sem framework externo, para manter consistente com o resto do projeto.
Reconcilia os valores calculados com as bases de origem de forma
independente do codigo de producao (recalcula do zero, nao chama
indicadores.py/sinalizacao.py), para pegar erros reais de calculo.

Como rodar:  python src/testes_indicadores.py
Retorna 0 se todos os testes passarem, 1 caso contrario.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config as cfg

resultados = []


def checar(nome: str, condicao: bool, detalhe: str = ""):
    resultados.append((nome, bool(condicao), detalhe))
    status = "PASS" if condicao else "FAIL"
    linha = f"  [{status}] {nome}"
    if detalhe:
        linha += f" - {detalhe}"
    print(linha)


def main() -> int:
    faltando = [p for p in (
        cfg.ARQ_BASE_BRUTA, cfg.ARQ_DESPESAS_TRATADA, cfg.ARQ_FAV_INFRA_BRUTO,
        cfg.ARQ_FAV_TRATADO, cfg.ARQ_DESPESAS_SINALIZADA,
    ) if not p.exists()]
    if faltando:
        print("Arquivos faltando, rode o pipeline completo antes:")
        for p in faltando:
            print(f"  {p}")
        return 1

    despesas_bruta = pd.read_parquet(cfg.ARQ_BASE_BRUTA)
    despesas_tratada = pd.read_parquet(cfg.ARQ_DESPESAS_TRATADA)
    fav_bruto = pd.read_parquet(cfg.ARQ_FAV_INFRA_BRUTO)
    fav_tratado = pd.read_parquet(cfg.ARQ_FAV_TRATADO)
    sinalizada = pd.read_parquet(cfg.ARQ_DESPESAS_SINALIZADA)

    print("=== Base de despesas ===")
    checar(
        "despesas_tratada tem 6 orgaos distintos",
        despesas_tratada["orgao"].nunique() == 6,
        f"encontrados: {despesas_tratada['orgao'].nunique()}",
    )
    checar(
        "despesas_tratada cobre a janela configurada de meses",
        despesas_tratada["ano_mes"].nunique() == cfg.MESES_JANELA,
        f"encontrados: {despesas_tratada['ano_mes'].nunique()}, esperado: {cfg.MESES_JANELA}",
    )
    checar(
        "tratamento preserva o valor total (bruto == tratada)",
        abs(despesas_bruta["valor"].sum() - despesas_tratada["valor"].sum()) < 0.01,
        f"bruto={despesas_bruta['valor'].sum():,.2f} tratada={despesas_tratada['valor'].sum():,.2f}",
    )
    checar(
        "despesas_tratada sem nulos nas colunas chave",
        despesas_tratada[["ano_mes", "area", "orgao", "valor"]].isna().sum().sum() == 0,
    )
    checar(
        "despesas_tratada.valor e sempre finito (sem inf/-inf/NaN)",
        despesas_tratada["valor"].apply(lambda v: v == v and abs(v) != float("inf")).all(),
    )

    print("\n=== Execucao por area (reconciliacao independente) ===")
    por_area = despesas_tratada.groupby("area")["valor"].sum()
    for area in ["saude", "educacao", "infraestrutura"]:
        checar(
            f"area '{area}' presente e com valor positivo",
            area in por_area.index and por_area[area] > 0,
            f"valor: R$ {por_area.get(area, 0):,.2f}",
        )

    print("\n=== Base de favorecidos ===")
    checar(
        "tratamento de favorecidos preserva o valor total (bruto == tratado)",
        abs(fav_bruto["valor"].sum() - fav_tratado["valor"].sum()) < 0.01,
        f"bruto={fav_bruto['valor'].sum():,.2f} tratado={fav_tratado['valor'].sum():,.2f}",
    )
    checar(
        "favorecidos_tratado cobre os 4 orgaos de infraestrutura",
        fav_tratado["codigo_orgao"].nunique() == 4,
        f"encontrados: {fav_tratado['codigo_orgao'].nunique()}",
    )

    maior_favorecido_independente = (
        fav_tratado.groupby("favorecido")["valor"].sum().sort_values(ascending=False).index[0]
    )
    checar(
        "maior favorecido recalculado bate com o esperado (Caixa Economica Federal)",
        maior_favorecido_independente == "CAIXA ECONOMICA FEDERAL",
        f"encontrado: {maior_favorecido_independente}",
    )

    print("\n=== Sinalizacao de atipicos ===")
    checar(
        "serie orgao x mes tem 36 linhas (6 orgaos x 6 meses)",
        len(sinalizada) == 36,
        f"encontrado: {len(sinalizada)}",
    )
    checar(
        "nenhuma variacao_pct sinalizada e infinita ou NaN",
        sinalizada.loc[sinalizada["atipico"], "variacao_pct"]
        .apply(lambda v: v == v and abs(v) != float("inf")).all(),
    )
    checar(
        "toda linha sinalizada realmente ultrapassa o limiar configurado",
        (sinalizada.loc[sinalizada["atipico"], "variacao_pct"].abs() > cfg.SINALIZACAO_LIMIAR_PCT).all(),
    )

    total = len(resultados)
    aprovados = sum(1 for _, ok, _ in resultados if ok)
    print(f"\n{aprovados}/{total} testes aprovados")
    if aprovados < total:
        print("\nFALHAS:")
        for nome, ok, detalhe in resultados:
            if not ok:
                print(f"  - {nome} ({detalhe})")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

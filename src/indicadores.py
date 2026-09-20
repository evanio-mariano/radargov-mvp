# -*- coding: utf-8 -*-
"""
INDICADORES - RadarGov (Sprint 2)

Calcula os indicadores do MVP a partir da base tratada de despesas:
  - execucao por area e por orgao (total do periodo)
  - serie historica mensal por area
  - variacao mensal por area (% em relacao ao mes anterior)

O ranking de favorecidos e calculado separadamente por
coleta_favorecidos.py (dados/tratado/ranking_favorecidos_infraestrutura.md),
porque depende de uma fonte diferente (API de favorecidos).

Como rodar:  python src/indicadores.py   (depois de tratamento.py)
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config as cfg


def main() -> int:
    if not cfg.ARQ_DESPESAS_TRATADA.exists():
        print(f"Base tratada nao encontrada: {cfg.ARQ_DESPESAS_TRATADA}")
        print("Rode antes: python src/tratamento.py")
        return 1

    df = pd.read_parquet(cfg.ARQ_DESPESAS_TRATADA)

    # --- 1. execucao por area (total do periodo) ---
    por_area = df.groupby("area", as_index=False)["valor"].sum().sort_values("valor", ascending=False)

    # --- 2. execucao por orgao (total do periodo) ---
    por_orgao = df.groupby(["area", "orgao"], as_index=False)["valor"].sum().sort_values("valor", ascending=False)

    # --- 3. serie historica mensal por area ---
    serie = df.groupby(["area", "ano_mes"], as_index=False)["valor"].sum().sort_values(["area", "ano_mes"])

    # --- 4. variacao mensal por area (% vs mes anterior) ---
    serie = serie.sort_values(["area", "ano_mes"])
    serie["valor_mes_anterior"] = serie.groupby("area")["valor"].shift(1)
    serie["variacao_pct"] = (serie["valor"] / serie["valor_mes_anterior"] - 1) * 100

    linhas = []
    linhas.append("# Caderno de indicadores - RadarGov")
    linhas.append("")
    linhas.append(f"Base: {cfg.ARQ_DESPESAS_TRATADA.name} | Periodo: {df['ano_mes'].min()} a {df['ano_mes'].max()}")
    linhas.append("")

    linhas.append("## 1. Execucao por area (total do periodo)")
    linhas.append("")
    linhas.append("Formula: soma de `valor` (Valor Pago) agrupado por `area`, no periodo completo.")
    linhas.append("")
    linhas.append("| Area | Valor (R$) |")
    linhas.append("|---|---|")
    for _, r in por_area.iterrows():
        linhas.append(f"| {r['area']} | {r['valor']:,.2f} |")
    linhas.append("")

    linhas.append("## 2. Execucao por orgao (total do periodo)")
    linhas.append("")
    linhas.append("Formula: soma de `valor` agrupado por `orgao`, no periodo completo.")
    linhas.append("")
    linhas.append("| Area | Orgao | Valor (R$) |")
    linhas.append("|---|---|---|")
    for _, r in por_orgao.iterrows():
        linhas.append(f"| {r['area']} | {r['orgao']} | {r['valor']:,.2f} |")
    linhas.append("")

    linhas.append("## 3. Serie historica mensal por area")
    linhas.append("")
    linhas.append("Formula: soma de `valor` agrupado por `area` e `ano_mes`.")
    linhas.append("")
    linhas.append("| Area | Mes | Valor (R$) |")
    linhas.append("|---|---|---|")
    for _, r in serie.iterrows():
        linhas.append(f"| {r['area']} | {r['ano_mes']} | {r['valor']:,.2f} |")
    linhas.append("")

    linhas.append("## 4. Variacao mensal por area")
    linhas.append("")
    linhas.append("Formula: `(valor do mes / valor do mes anterior - 1) x 100`. "
                   "O primeiro mes de cada area nao tem mes anterior na janela "
                   "coletada, por isso fica sem variacao calculada.")
    linhas.append("")
    linhas.append("Exemplo: se educacao pagou R$ 20 mi em 2026-04 e R$ 22 mi em "
                   "2026-05, a variacao de maio e (22/20 - 1) x 100 = +10,0%.")
    linhas.append("")
    linhas.append("| Area | Mes | Valor (R$) | Variacao vs mes anterior |")
    linhas.append("|---|---|---|---|")
    for _, r in serie.iterrows():
        var = "-" if pd.isna(r["variacao_pct"]) else f"{r['variacao_pct']:+.1f}%"
        linhas.append(f"| {r['area']} | {r['ano_mes']} | {r['valor']:,.2f} | {var} |")
    linhas.append("")

    linhas.append("## 5. Ranking de favorecidos")
    linhas.append("")
    linhas.append("Calculado separadamente, ver "
                   f"`{cfg.ARQ_FAV_INFRA_RANKING.name}` (escopo: area infraestrutura, "
                   "ver DICIONARIO_DE_DADOS.md para a justificativa).")

    cfg.ARQ_CADERNO_INDICADORES.write_text("\n".join(linhas), encoding="utf-8")

    print(f"Caderno de indicadores salvo em: {cfg.ARQ_CADERNO_INDICADORES}")
    print("\nExecucao por area:")
    for _, r in por_area.iterrows():
        print(f"  {r['area']:15} R$ {r['valor']:>18,.2f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

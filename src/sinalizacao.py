# -*- coding: utf-8 -*-
"""
SINALIZACAO DE DESPESA ATIPICA - RadarGov (Sprint 2)

Regra estatistica simples (nao e classificacao automatica nem ML, por
decisao de escopo do MVP - ver Restricoes na Secao 3.2.5 do relatorio):
para cada orgao, calcula a variacao percentual do total pago de um mes
para o outro e marca como "atipico" quando o modulo da variacao
ultrapassa config.SINALIZACAO_LIMIAR_PCT.

A regra roda no nivel orgao (nao orgao+funcao): a serie mensal por
orgao e densa (todo orgao tem valor em todos os meses da janela), o que
evita comparar meses que nao sao realmente consecutivos e divisoes por
zero que aconteceriam no nivel funcao, onde muitas combinacoes so
aparecem em alguns meses.

Isso NAO significa irregularidade - e so um destaque para revisao
humana, com o valor e o mes anterior sempre visiveis ao lado (ver nota
metodologica).

Como rodar:  python src/sinalizacao.py   (depois de tratamento.py)
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

    # agrega ao nivel orgao (serie densa: todo orgao tem os 6 meses)
    por_orgao_mes = (
        df.groupby(["area", "orgao", "ano_mes"], as_index=False)["valor"].sum()
        .sort_values(["area", "orgao", "ano_mes"])
        .reset_index(drop=True)
    )

    grupo = por_orgao_mes.groupby(["area", "orgao"])["valor"]
    por_orgao_mes["valor_mes_anterior"] = grupo.shift(1)
    por_orgao_mes["variacao_pct"] = (
        por_orgao_mes["valor"] / por_orgao_mes["valor_mes_anterior"] - 1
    ) * 100
    por_orgao_mes["atipico"] = por_orgao_mes["variacao_pct"].abs() > cfg.SINALIZACAO_LIMIAR_PCT
    por_orgao_mes["atipico"] = por_orgao_mes["atipico"].fillna(False)

    cfg.DIR_TRATADO.mkdir(parents=True, exist_ok=True)
    por_orgao_mes.to_parquet(cfg.ARQ_DESPESAS_SINALIZADA, index=False)

    atipicos = por_orgao_mes[por_orgao_mes["atipico"]].sort_values(
        "variacao_pct", key=lambda s: s.abs(), ascending=False
    )

    linhas = []
    linhas.append("# Relatorio de despesas sinalizadas - RadarGov")
    linhas.append("")
    linhas.append(f"Regra: variacao percentual mes a mes acima de {cfg.SINALIZACAO_LIMIAR_PCT}% "
                   "(em modulo) no total pago por orgao. Calculado sobre a serie mensal "
                   "por orgao (densa - todo orgao tem os 6 meses da janela).")
    linhas.append("")
    linhas.append("Uma sinalizacao NAO significa irregularidade - e apenas um destaque "
                   "estatistico simples para revisao humana antes de qualquer comunicacao "
                   "publica (ver nota metodologica).")
    linhas.append("")
    linhas.append(f"Total de linhas avaliadas: {len(por_orgao_mes)} | Sinalizadas: {len(atipicos)}")
    linhas.append("")
    linhas.append("| Area | Orgao | Mes | Valor (R$) | Mes anterior (R$) | Variacao |")
    linhas.append("|---|---|---|---|---|---|")
    for _, r in atipicos.iterrows():
        linhas.append(
            f"| {r['area']} | {r['orgao']} | {r['ano_mes']} | "
            f"{r['valor']:,.2f} | {r['valor_mes_anterior']:,.2f} | {r['variacao_pct']:+.1f}% |"
        )

    cfg.ARQ_RELATORIO_ATIPICOS.write_text("\n".join(linhas), encoding="utf-8")

    print(f"Base sinalizada salva em: {cfg.ARQ_DESPESAS_SINALIZADA}")
    print(f"Relatorio salvo em      : {cfg.ARQ_RELATORIO_ATIPICOS}")
    print(f"\n{len(atipicos)} de {len(por_orgao_mes)} linhas sinalizadas (limiar: {cfg.SINALIZACAO_LIMIAR_PCT}%)")
    for _, r in atipicos.iterrows():
        print(f"  {r['area']:15} {r['orgao']:30} {r['ano_mes']}  {r['variacao_pct']:+.1f}%")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

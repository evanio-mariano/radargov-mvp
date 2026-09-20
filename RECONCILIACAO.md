# Checklist de reconciliacao - RadarGov (Sprint 2)

Confere um numero calculado pelo pipeline contra uma consulta manual
direta no site do Portal da Transparencia, para validar que os
indicadores batem com a fonte.

## Item verificado

**Ministerio da Saude, agosto/2026, Valor Pago total.**

- Fonte oficial (consulta manual em
  https://portaldatransparencia.gov.br/despesas/consulta, filtro Periodo
  08/2026 a 08/2026 + Orgao executor = Ministerio da Saude, painel
  grafico "Valor Pago de Despesas por Mes Ano"): **R$ 18.470.583.301,91**
- Pipeline RadarGov (despesas_tratada.parquet): **R$ 18.470.583.301,91**
- Resultado: **bateu exato**, ate o centavo.

## Achado durante a reconciliacao

Na primeira tentativa, o pipeline mostrava R$ 18.928.730.140,77 - uma
diferenca de ~R$ 458 milhoes (2,4%) em relacao ao Portal. A causa: a
base local usada no teste havia sido baixada ~10 dias antes e o Portal
havia revisado os valores de agosto/2026 nesse intervalo (comum em
dados de execucao orcamentaria - lancamentos atrasados, correcoes).
Apos rodar `python src/coleta.py` de novo (baixando os arquivos
atualizados), o numero do pipeline passou a bater exatamente com o
Portal.

**Isso reforca, com evidencia concreta, a decisao de manter a carga
automatizada diaria** (Secao 3.2.2 do relatorio): a fonte muda depois
da primeira publicacao, e so uma coleta recorrente mantem a base
confiavel. Tambem e evidencia empirica para a parte da hipotese H2
("atualizacao suficiente") que havia ficado marcada como nao testada
apos a Sprint 1 (ver Secao 4.1.2 do relatorio).

## Proximos itens sugeridos (fora do escopo desta checagem pontual)

- Repetir a reconciliacao para outro orgao/mes antes da homologacao
  final (Sprint 4), para confirmar que o resultado nao foi coincidencia.
- Monitorar, ao longo das proximas semanas, se as execucoes diarias do
  GitHub Actions realmente absorvem essas revisoes automaticamente (o
  commit "Atualizacao automatica da base" deve mudar de tamanho quando
  isso acontecer).

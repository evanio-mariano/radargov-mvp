# Nota metodologica - RadarGov (Sprint 2)

Premissas e ressalvas de interpretacao dos indicadores do MVP. Leitura
recomendada antes de qualquer uso publico dos numeros do RadarGov.

## 1. Medida de gasto usada

Os indicadores de despesas por area/orgao usam **Valor Pago (R$)** da
Execucao da Despesa - o desembolso efetivo, nao o valor comprometido
(empenhado) nem apenas liquidado. Ver DICIONARIO_DE_DADOS.md.

## 2. Os totais de "despesas" e de "favorecidos" nao batem entre si - e esperado

O total de despesas de infraestrutura no periodo (R$ 62,6 bi,
despesas_tratada.parquet) e **menor** que o total recebido por
favorecidos de infraestrutura no mesmo periodo (R$ 74,5 bi,
favorecidos_tratado.parquet). Isso nao e um erro de calculo (os testes
automatizados confirmam que cada base preserva corretamente o total da
sua propria fonte) - as duas vem de **conjuntos de dados diferentes** do
Portal da Transparencia, com bases contabeis proprias:

- `despesas_tratada` vem da Execucao da Despesa (foco orcamentario:
  empenho, liquidacao, pagamento por classificacao funcional).
- `favorecidos_tratado` vem do endpoint de Recebimento de Recursos por
  Favorecido (foco no movimento financeiro por quem recebeu, que pode
  incluir restos a pagar de exercicios anteriores pagos no periodo e
  outras movimentacoes que nao aparecem com a mesma classificacao na
  Execucao da Despesa).

Os dois indicadores devem ser lidos e comunicados **separadamente**: um
mede "quanto o orgao pagou por funcao de governo", o outro mede "quanto
cada favorecido recebeu". Nao devem ser somados nem comparados linha a
linha sem essa ressalva.

## 3. Ranking de favorecidos cobre so infraestrutura

Saude e educacao tem volume de favorecidos por mes muito maior que
infraestrutura (medido na Sprint 2 - ver DICIONARIO_DE_DADOS.md) e
ficaram fora do MVP por restricao de tempo, nao por decisao de que sao
menos relevantes. Fica registrado como evolucao futura do produto.

## 4. "SEM INFORMACAO" e "FOLHA DE PAGAMENTO" como favorecido

Alguns registros do Portal nao identificam o favorecido individualmente
(aparecem como "SEM INFORMACAO") ou o agregam como "FOLHA DE PAGAMENTO"
(provavelmente remuneracao de pessoal, sem abrir por pessoa). Isso e uma
limitacao da fonte, nao um erro do pipeline - esses valores continuam
somados nos totais, mas nao podem ser atribuidos a um favorecido
especifico no ranking.

## 5. Valores negativos em favorecidos (estornos/devolucoes)

615 combinacoes (mes x orgao x favorecido) em favorecidos_tratado tem
valor liquido negativo - a fonte registra estornos e devolucoes que, no
periodo, superaram os recebimentos. Esses valores sao mantidos (nao
filtrados), para nao inflar artificialmente o total do periodo.

## 6. Sinalizacao de despesa atipica nao e deteccao de irregularidade

A sinalizacao (src/sinalizacao.py) usa uma regra estatistica simples
(variacao percentual mes a mes acima de um limiar, no nivel orgao) para
destacar meses que fogem do padrao recente daquele orgao. **Nao ha
nenhuma inferencia sobre causa** - uma sinalizacao pode refletir
sazonalidade normal do orgao (ex.: pagamento concentrado em determinado
mes do ano), inicio/fim de um programa, ou de fato algo que mereça
verificacao. Toda sinalizacao deve ser revisada por uma pessoa antes de
qualquer comunicacao publica. A deteccao automatizada por algoritmos de
anomalia (hipotese H3, Secao 2.4) segue fora do escopo deste MVP.

## 7. Dados de execucao orcamentaria sao revisados apos a publicacao

Na reconciliacao da Sprint 2 (ver RECONCILIACAO.md), um numero
calculado pelo pipeline ficou ~2,4% diferente do site oficial porque a
base local havia sido baixada dias antes, e o Portal revisou os valores
do mes no intervalo. Apos coletar novamente, o numero bateu exato. Isso
confirma que a janela de dados do RadarGov deve ser sempre a mais
recente possivel (dai a carga diaria automatizada) - um numero
"antigo" do pipeline pode ficar desatualizado mesmo sem nenhum erro no
calculo.

## 8. Janela de dados

Os indicadores cobrem os ultimos 6 meses completos disponiveis no
momento da coleta (config.MESES_JANELA), nao os 24 meses previstos na
concepcao original da solucao (Secao 3.2.5) - a ampliacao fica para uma
proxima etapa, apos a validacao do pipeline com a janela menor.

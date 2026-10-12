# RadarGov (MVP) - versão 1.0

Monitoramento de despesas diretas da União a partir do Portal da Transparência,
desenvolvido como Projeto Final de Curso do MBA (IBMEC). O RadarGov coleta,
trata e reconcilia os dados todos os dias e os entrega em um dashboard com
duas visões: **executiva** (indicadores-chave) e **operacional** (filtros,
variação mensal, ranking de favorecidos e download dos dados).

**Escopo do MVP:** 6 órgãos superiores (Saúde, Educação, Transportes, Cidades,
Integração e Desenvolvimento Regional, Portos e Aeroportos), janela de
03/2026 a 08/2026, medida Valor Pago. O ranking de favorecidos cobre apenas a
área de infraestrutura.

## O que o pipeline faz

```
coleta.py            baixa os arquivos mensais de Execução da Despesa
qualidade.py         valida o schema e gera o relatório de qualidade
tratamento.py        limpa, padroniza órgãos e cria a base curada
indicadores.py       calcula os indicadores (caderno_indicadores.md)
sinalizacao.py       marca variações mensais atípicas (> 50%)
exporta_powerbi.py   grava os 6 CSV que o dashboard lê
testes_indicadores.py  testes automatizados, reconciliáveis com a fonte
coleta_favorecidos.py  ranking de favorecidos da infraestrutura (semanal)
```

## Estrutura do repositório

```
config.py                    configurações (único arquivo de ajuste)
de_para_orgao_area.csv       mapeamento órgão -> área (por código do órgão)
requirements.txt             bibliotecas Python
src/                         scripts do pipeline
dados/bruto/                 bases brutas em Parquet
dados/tratado/               bases tratadas e relatórios (md)
dados/tratado/powerbi/       CSV consumidos pelo dashboard
dashboard/                   arquivo .pbix e guia de construção
homologacao/                 roteiro, planilha de registro e resultados da Sprint 4
.github/workflows/           automação (GitHub Actions)
```

Documentação: `DICIONARIO_DE_DADOS.md`, `MODELO_DE_DADOS.md`,
`NOTA_METODOLOGICA.md` e `RECONCILIACAO.md`.

## Automação (GitHub Actions)

| Workflow | Frequência | O que roda |
|---|---|---|
| `pipeline.yml` | diária, 06:00 UTC (03:00 em Brasília) | coleta, qualidade, tratamento, indicadores, sinalização, exportação para o Power BI, testes e commit da base |
| `favorecidos.yml` | semanal, domingo 07:00 UTC | coleta paginada de favorecidos da infraestrutura (API do Portal) |

O workflow de favorecidos usa o segredo `PORTAL_API_KEY` (chave da API do
Portal da Transparência), cadastrado em *Settings > Secrets and variables >
Actions*. O robô precisa de permissão de escrita em *Settings > Actions >
General > Workflow permissions*.

## Como rodar no computador

1. Instale o Python 3.11 ou mais novo (marque "Add python.exe to PATH").
2. Na pasta do projeto: `pip install -r requirements.txt`
3. Rode, nesta ordem: `python src/coleta.py`, `python src/qualidade.py`,
   `python src/tratamento.py`, `python src/indicadores.py`,
   `python src/sinalizacao.py`, `python src/exporta_powerbi.py` e
   `python src/testes_indicadores.py`.
4. Para os favorecidos, crie um arquivo `.env` com `PORTAL_API_KEY=...` e rode
   `python src/coleta_favorecidos.py` (leva cerca de uma hora).

## Dashboard

O arquivo `dashboard/RadarGov_Dashboard.pbix` lê os CSV de
`dados/tratado/powerbi/` diretamente deste repositório. O passo a passo de
construção está em `dashboard/GUIA_DASHBOARD.md`. Ao abrir o arquivo, use
*Atualizar* para carregar a base mais recente.

## Homologação (Sprint 4)

A pasta `homologacao/` reúne o roteiro, a planilha de registro de tempos e
respostas e os resultados. Resumo: nas quatro tarefas de análise testadas, o
tempo caiu de 37 min 21 s (processo manual no Portal) para 2 min 47 s com o
RadarGov. O teste foi conduzido pelo próprio autor, nos dois papéis; é um
teste de viabilidade, não uma validação estatística com usuários.

## Limitações conhecidas

- Ranking de favorecidos apenas para infraestrutura (o volume de saúde e
  educação inviabilizou a coleta completa no MVP).
- Janela de 6 meses (o plano previa 24).
- Detecção automatizada de anomalias (hipótese H3) fica para a versão 2; a
  sinalização atual é uma regra estatística simples e não indica irregularidade.
- Publicação do dashboard na Web depende de conta institucional do Power BI.
- O Portal revisa valores já publicados; a carga diária absorve essas revisões.

## Fonte e uso dos dados

Dados do Portal da Transparência do Governo Federal (CGU), publicados com base
na Lei de Acesso à Informação. O CPF de pessoas físicas é exibido parcialmente
mascarado, como na fonte.

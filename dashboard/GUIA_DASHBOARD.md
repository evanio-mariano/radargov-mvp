# Guia de construcao do dashboard RadarGov (Sprint 3)

Dashboard em Power BI Desktop, alimentado pelos CSV que o pipeline publica em
`dados/tratado/powerbi/` (ver MODELO_DE_DADOS.md). Duas paginas, uma por perfil:
**Visao Executiva** (Dep. Fernanda Costa) e **Visao Operacional** (Rafael Andrade).

Paleta do relatorio: azul-marinho `#002060`, azul `#2E74B5`, azul-claro `#D9E2F3`,
cinza `#7A7A7A`, alerta `#E8A33D`.

---

## Parte 1. Conectar os dados

Pre-requisito: os CSV precisam estar no GitHub (rode o workflow "RadarGov - pipeline
de ingestao" uma vez apos subir os arquivos novos).

No Power BI Desktop: **Pagina Inicial > Obter dados > Consulta em branco**, abra
**Editor Avancado**, apague o conteudo e cole uma consulta por vez. Renomeie cada
consulta com o nome indicado (clique com o botao direito > Renomear).

Todas usam o mesmo padrao (`Web.Contents` com `RelativePath`, que permite atualizacao
automatica no servico do Power BI).

### despesas

```
let
    Fonte = Csv.Document(
        Web.Contents("https://raw.githubusercontent.com/evanio-mariano/radargov-mvp/main/",
            [RelativePath = "dados/tratado/powerbi/despesas.csv"]),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Cabecalho = Table.PromoteHeaders(Fonte, [PromoteAllScalars = true]),
    Tipos = Table.TransformColumnTypes(Cabecalho, {
        {"ano_mes", type text}, {"ano", Int64.Type}, {"mes", Int64.Type},
        {"area", type text}, {"codigo_orgao", type text}, {"orgao", type text},
        {"funcao", type text}, {"valor", type number}}, "en-US")
in
    Tipos
```

### favorecidos

```
let
    Fonte = Csv.Document(
        Web.Contents("https://raw.githubusercontent.com/evanio-mariano/radargov-mvp/main/",
            [RelativePath = "dados/tratado/powerbi/favorecidos.csv"]),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Cabecalho = Table.PromoteHeaders(Fonte, [PromoteAllScalars = true]),
    Tipos = Table.TransformColumnTypes(Cabecalho, {
        {"ano_mes", type text}, {"ano", Int64.Type}, {"mes", Int64.Type},
        {"area", type text}, {"codigo_orgao", type text}, {"orgao", type text},
        {"codigo_favorecido", type text}, {"favorecido", type text},
        {"tipo_favorecido", type text}, {"valor", type number}}, "en-US")
in
    Tipos
```

### sinalizacao

```
let
    Fonte = Csv.Document(
        Web.Contents("https://raw.githubusercontent.com/evanio-mariano/radargov-mvp/main/",
            [RelativePath = "dados/tratado/powerbi/sinalizacao.csv"]),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Cabecalho = Table.PromoteHeaders(Fonte, [PromoteAllScalars = true]),
    Tipos = Table.TransformColumnTypes(Cabecalho, {
        {"area", type text}, {"codigo_orgao", type text}, {"orgao", type text},
        {"ano_mes", type text}, {"valor", type number},
        {"valor_mes_anterior", type number}, {"variacao_pct", type number},
        {"atipico", type text}, {"atipico_flag", Int64.Type}}, "en-US")
in
    Tipos
```

### dim_orgao

```
let
    Fonte = Csv.Document(
        Web.Contents("https://raw.githubusercontent.com/evanio-mariano/radargov-mvp/main/",
            [RelativePath = "dados/tratado/powerbi/dim_orgao.csv"]),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Cabecalho = Table.PromoteHeaders(Fonte, [PromoteAllScalars = true]),
    Tipos = Table.TransformColumnTypes(Cabecalho, {
        {"codigo_orgao", type text}, {"orgao", type text}, {"area", type text}}, "en-US")
in
    Tipos
```

### dim_tempo

```
let
    Fonte = Csv.Document(
        Web.Contents("https://raw.githubusercontent.com/evanio-mariano/radargov-mvp/main/",
            [RelativePath = "dados/tratado/powerbi/dim_tempo.csv"]),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Cabecalho = Table.PromoteHeaders(Fonte, [PromoteAllScalars = true]),
    Tipos = Table.TransformColumnTypes(Cabecalho, {
        {"ano_mes", type text}, {"data", type date}, {"ano", Int64.Type},
        {"mes", Int64.Type}, {"indice_mes", Int64.Type}, {"mes_rotulo", type text}}, "en-US")
in
    Tipos
```

### metadados

```
let
    Fonte = Csv.Document(
        Web.Contents("https://raw.githubusercontent.com/evanio-mariano/radargov-mvp/main/",
            [RelativePath = "dados/tratado/powerbi/metadados.csv"]),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Cabecalho = Table.PromoteHeaders(Fonte, [PromoteAllScalars = true]),
    Tipos = Table.TransformColumnTypes(Cabecalho, {
        {"atualizado_em", type datetime}, {"atualizado_em_texto", type text},
        {"periodo_inicio", type text}, {"periodo_fim", type text},
        {"linhas_despesas", Int64.Type}, {"linhas_favorecidos", Int64.Type},
        {"fonte", type text}}, "en-US")
in
    Tipos
```

Se o Power BI pedir credenciais da fonte: **Anonimo**, nivel `https://raw.githubusercontent.com/`.
Depois clique em **Fechar e Aplicar**.

---

## Parte 2. Modelo (aba Modelo)

Relacionamentos (um para muitos, direcao unica, da dimensao para o fato):

| De (um) | Para (muitos) |
|---|---|
| dim_tempo[ano_mes] | despesas[ano_mes], favorecidos[ano_mes], sinalizacao[ano_mes] |
| dim_orgao[codigo_orgao] | despesas[codigo_orgao], favorecidos[codigo_orgao], sinalizacao[codigo_orgao] |

`metadados` fica sem relacionamento.

Ordenacao: selecione `dim_tempo[mes_rotulo]` > **Ferramentas de coluna > Classificar por
coluna > indice_mes**.

Ocultar colunas tecnicas (`ano`, `mes`, `indice_mes`, `atipico_flag`) do modo de exibicao de
relatorio, para nao poluir a lista de campos.

---

## Parte 3. Medidas (DAX)

Crie uma tabela para as medidas: **Inserir dados**, uma coluna qualquer, nome da tabela
`_Medidas`, carregar. Depois **Nova medida** para cada item.

```
Total Pago = SUM ( despesas[valor] )

Total Pago (bi) = DIVIDE ( [Total Pago], 1000000000 )

Participacao na Area % =
DIVIDE ( [Total Pago], CALCULATE ( [Total Pago], REMOVEFILTERS ( despesas[area] ) ) )

Valor Mes Anterior =
VAR _i = MAX ( dim_tempo[indice_mes] )
RETURN CALCULATE ( [Total Pago], REMOVEFILTERS ( dim_tempo ), dim_tempo[indice_mes] = _i - 1 )

Variacao Mensal % =
VAR _ant = [Valor Mes Anterior]
RETURN IF ( NOT ISBLANK ( _ant ), DIVIDE ( [Total Pago] - _ant, _ant ) )

N Orgaos = DISTINCTCOUNT ( despesas[codigo_orgao] )

N Sinalizacoes = SUM ( sinalizacao[atipico_flag] )

Total Recebido (favorecidos) = SUM ( favorecidos[valor] )

N Favorecidos = DISTINCTCOUNT ( favorecidos[codigo_favorecido] )

Ultima Atualizacao = "Dados atualizados em " & SELECTEDVALUE ( metadados[atualizado_em_texto] )
```

Se o Power BI reclamar dos separadores nas formulas, troque as virgulas entre argumentos por ponto e virgula.

Formatos (**Ferramentas de medida > Formato**, escolha "Personalizado" e digite):

| Medida | Formato |
|---|---|
| Total Pago (bi) | `"R$ "0.0" bi"` |
| Total Pago, Total Recebido (favorecidos) | `"R$ "#,0.00,,," bi"` |
| Participacao na Area %, Variacao Mensal % | porcentagem, 1 casa decimal |

A variacao mensal so faz sentido com **um mes selecionado** (o primeiro mes da janela nao
tem mes anterior e fica em branco).

---

## Parte 4. Pagina 1: Visao Executiva (perfil Fernanda Costa)

Nome da pagina: `Visao Executiva`. Fundo branco, titulo em `#002060`.

| Elemento | Visual | Campos |
|---|---|---|
| Titulo e subtitulo | Caixa de texto | "RadarGov | Despesas federais em saude, educacao e infraestrutura" |
| Data da atualizacao | Cartao | `Ultima Atualizacao` |
| Filtros | 2 segmentacoes (lista, horizontal) | `dim_tempo[mes_rotulo]`, `dim_orgao[area]` |
| Total no periodo | Cartao | `Total Pago (bi)` |
| Orgaos monitorados | Cartao | `N Orgaos` |
| Despesas sinalizadas | Cartao | `N Sinalizacoes` |
| Execucao por area | Barras horizontais | Eixo `dim_orgao[area]`, valor `Total Pago (bi)`, dica `Participacao na Area %` |
| Evolucao mensal | Linhas | Eixo `dim_tempo[mes_rotulo]`, valor `Total Pago (bi)`, legenda `dim_orgao[area]` |
| Sinalizacoes | Tabela | `sinalizacao[orgao]`, `dim_tempo[mes_rotulo]`, `sinalizacao[valor]`, `sinalizacao[variacao_pct]`; filtro do visual: `sinalizacao[atipico]` = Sim |
| Ressalvas | Caixa de texto | Texto fixo (abaixo) |

Texto fixo de contexto e ressalvas (usar nas duas paginas):

> Valores em reais pagos pelo Governo Federal (Valor Pago), por órgão superior. Fonte: Portal da Transparência.
> A sinalização marca variações mensais acima de 50% no total pago por órgão. É um destaque estatístico simples, não indica irregularidade.
> O ranking de favorecidos cobre apenas a área infraestrutura: o volume de saúde e educação inviabilizou a coleta completa neste MVP.
> Nomes de pessoa física seguem o mesmo padrão de divulgação do Portal da Transparência (Lei de Acesso à Informação), com CPF parcialmente mascarado pela fonte.
> A fonte pode revisar valores de meses recentes depois da publicação.

---

## Parte 5. Pagina 2: Visao Operacional (perfil Rafael Andrade)

Nome da pagina: `Visao Operacional`.

| Elemento | Visual | Campos |
|---|---|---|
| Filtros | 4 segmentacoes | `dim_tempo[mes_rotulo]`, `dim_orgao[area]`, `dim_orgao[orgao]`, `favorecidos[tipo_favorecido]` |
| Busca de favorecido | Segmentacao (lista com busca) | `favorecidos[favorecido]` |
| Data da atualizacao | Cartao | `Ultima Atualizacao` |
| Despesa por orgao e funcao | Tabela | `dim_orgao[orgao]`, `despesas[funcao]`, `Total Pago` |
| Variacao mensal por orgao | Matriz | Linhas `dim_orgao[orgao]`, colunas `dim_tempo[mes_rotulo]`, valores `Variacao Mensal %` (formatacao condicional: vermelho acima de 50%, azul abaixo de -50%) |
| Ranking de favorecidos (infraestrutura) | Barras horizontais | Eixo `favorecidos[favorecido]`, valor `Total Recebido (favorecidos)`, filtro do visual: **N principais = 15** por `Total Recebido (favorecidos)` |
| Detalhe dos favorecidos | Tabela | `favorecidos[favorecido]`, `favorecidos[codigo_favorecido]`, `favorecidos[tipo_favorecido]`, `Total Recebido (favorecidos)` |
| Download dos dados | 3 botoes (Botao > Em branco), acao **URL da Web** | links abaixo |
| Ressalvas | Caixa de texto | Mesmo texto fixo da pagina 1 |

Links dos botoes de download (o menu "Exportar dados" nao funciona em relatorios
publicados na web, por isso os botoes apontam para os CSV do repositorio):

- Despesas: `https://raw.githubusercontent.com/evanio-mariano/radargov-mvp/main/dados/tratado/powerbi/despesas.csv`
- Favorecidos: `https://raw.githubusercontent.com/evanio-mariano/radargov-mvp/main/dados/tratado/powerbi/favorecidos.csv`
- Sinalizacoes: `https://raw.githubusercontent.com/evanio-mariano/radargov-mvp/main/dados/tratado/powerbi/sinalizacao.csv`

Decisao sobre dados pessoais (LGPD, item da Tabela 5 do relatorio): Pessoa Física
entra no ranking e no detalhe, sem filtro. Isso e defensavel porque o Portal da
Transparencia ja publica esses mesmos nomes e valores por forca da Lei de Acesso
a Informacao (LAI); o RadarGov nao revela nada que a fonte oficial nao revele. O
`codigo_favorecido` exibido e sempre o CPF ja mascarado pelo proprio Portal na
origem (formato `***.573.123-**`) - nunca crie nem exiba uma versao sem mascara.

---

## Parte 6. Usabilidade e identidade visual (tarefa da Sprint 3)

- Uma mensagem por visual: titulo curto e claro em cada grafico, com unidade (R$ bi).
- Cores: azul `#2E74B5` como cor principal, `#E8A33D` so para alertas e sinalizacoes.
- Fonte minima de 12 pt nos textos e 10 pt nos rotulos; contraste alto (texto escuro em fundo claro).
- No maximo 8 visuais por pagina; alinhar tudo a grade (Formatar > Propriedades > Grade).
- Texto alternativo em cada visual (Formatar > Geral > Texto alternativo).
- Ordem de tabulacao logica (Exibir > Painel de selecao > Ordem de tabulacao).
- Navegacao: botoes "Visao Executiva" e "Visao Operacional" (Inserir > Botoes > Navegador de paginas).
- Teste rapido com uma pessoa nao tecnica: ela acha o total do periodo e as sinalizacoes em menos de 30 segundos?

---

## Parte 7. Publicar

1. **Pagina Inicial > Publicar** e escolher o workspace (Meu workspace).
2. No servico (app.powerbi.com): abrir o relatorio > **Arquivo > Inserir relatorio > Publicar na Web (publico)** > **Criar codigo de insercao**. O link gerado e o "endereco do MVP no ar".
3. Configurar a atualizacao diaria: conjunto de dados > **Configuracoes > Credenciais da fonte de dados** (Anonimo) > **Atualizacao agendada** (uma vez por dia, por exemplo as 05:00 de Brasilia; o pipeline roda as 03:00 e leva menos de 1 minuto).

Requisitos (Microsoft Learn, "Publish to web"): conta do servico Power BI (e-mail
institucional ou de trabalho, nao aceita Gmail pessoal) e a opcao "Publicar na Web"
habilitada pelo administrador do tenant.

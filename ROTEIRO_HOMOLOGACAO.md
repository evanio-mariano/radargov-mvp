# Roteiro de homologação do RadarGov (Sprint 4)

Objetivo: medir, com o mesmo conjunto de perguntas, quanto tempo leva
responder usando só o Portal da Transparência (Rodada 1) e usando o
dashboard RadarGov (Rodada 2), para testar a hipótese **H1** (redução de
pelo menos 50% do tempo de análise), e registrar a satisfação e os
defeitos encontrados, para a hipótese **H4** (adoção).

Quem executa: o próprio autor, nos dois papéis (analista que usa o processo
manual e analista que usa o dashboard). Não há equipe real de assessoria.
Essa limitação precisa constar no relatório (ver seção "Limitações").

---

## 1. Regras do experimento (valem para as duas rodadas)

| Item | Regra |
|---|---|
| Período | Sempre **03/2026 a 08/2026** (mesma janela do dashboard) |
| Medida | **Valor Pago** (nunca empenhado ou liquidado) |
| Órgãos | Os 6 órgãos do MVP: Ministério da Saúde, Ministério da Educação, Ministério dos Transportes, Ministério das Cidades, Ministério da Integração e do Desenvolvimento Regional, Ministério de Portos e Aeroportos |
| Cronômetro | Use o cronômetro do celular. Inicia ao terminar de ler a pergunta; para quando a resposta estiver escrita na ficha |
| Tempo máximo | **20 min por tarefa**. Estourou: pare, anote "não concluída" e o que já tinha |
| Reaproveitar números | Pode, se já estiverem na sua ficha (um analista faria o mesmo). Anote "reaproveitei da T_" |
| Datas de atualização | Antes de começar, anote a data do Portal ("Dados atualizados até") e a do dashboard ("Dados atualizados em") |
| Arredondamento | Valores em R$ com 2 casas; percentuais com 1 casa |

### Por que há duas variantes (A e B) de cada pergunta

Se você repetir a mesma pergunta na Rodada 2, já vai saber a resposta e o
tempo do dashboard ficará artificialmente menor. Por isso a Rodada 1 usa a
variante **A** e a Rodada 2 usa a variante **B**, com o mesmo grau de
dificuldade.

---

## 2. As 4 tarefas

| # | Variante A (Rodada 1: só Portal) | Variante B (Rodada 2: só dashboard) |
|---|---|---|
| T1 | Qual o **total pago** pelo **Ministério da Saúde** em **ago/2026**? | Qual o **total pago** pelo **Ministério da Educação** em **jul/2026**? |
| T2 | Entre **Saúde, Educação e Transportes**, qual teve a **maior variação percentual** (em módulo) de um mês para o seguinte, entre mar e ago/2026? Informe o órgão, o mês e o percentual. | Entre **Cidades, Integração e Portos e Aeroportos**, idem. |
| T3 | Quais os **5 maiores favorecidos** (soma de mar a ago/2026) do **Ministério dos Transportes**? | Idem para o **Ministério das Cidades**. |
| T4 | Qual a **participação percentual** do **Ministério da Educação** no total pago pelos 6 órgãos em mar-ago/2026? | Idem para o **Ministério da Saúde**. |

Observações:
- T2: o primeiro mês (mar/2026) não tem mês anterior; há 5 variações por órgão (abr a ago).
- T3: no Portal, o mesmo favorecido aparece em várias linhas (uma por mês); é preciso somar.
- T4: o denominador é a soma dos 6 órgãos no período inteiro.

---

## 3. Rodada 1 (processo manual, só o Portal)

Feche ou não abra o dashboard. Tenha à mão uma planilha (Excel) para somar
e calcular percentuais, como uma assessoria faria.

### Passo a passo do Portal (telas conferidas em 08/10/2026)

**T1, T2 e T4: total pago por órgão e mês**

1. Abra https://portaldatransparencia.gov.br/despesas/consulta
2. Clique no botão **Período**. Em **Início** digite `03/2026`, em **Fim**
   digite `08/2026` e clique em **Adicionar**. Use sempre esse período
   para T1, T2 e T4 (em T1, basta ler o valor de ago/2026).
3. Clique no botão **Órgão executor**. A caixa de texto começa vazia e a
   lista **só aparece depois que você digita**. Digite a palavra indicada
   na tabela abaixo, espere 1 a 2 segundos e clique na linha que termina
   com **(Órgão superior)**. Não escolha as linhas "- Unidades com vínculo
   direto", nem fundações, agências ou unidades gestoras. Depois clique em
   **Adicionar**.
4. **Não use o botão "Painel Gráfico" do topo:** ele leva à página geral
   do Governo (valores do ano inteiro, sem órgão nem mês). Role a página
   de consulta até o fim, até o bloco **Visualização gráfica**. Em
   **Tipo de Dados**, marque **Mês ano**; em **Valor apresentado**, escolha
   **Pago**; em **Tipo de gráfico**, **Barras**; clique em **Gerar Gráfico**.
   O gráfico "Valor Pago de Despesas por Mês Ano" é o que bateu exatamente
   com o pipeline na reconciliação da Sprint 2 (Saúde/ago-2026 =
   R$ 18.470.583.301,91 na época).
5. Anote o Valor Pago de cada mês na ficha.
6. Para T2 e T4, repita para cada órgão (um órgão por consulta).

O que digitar e qual linha escolher (nomes conferidos na tela em 09/10/2026):

| Para escolher | Digite | Clique na linha |
|---|---|---|
| Saúde | `Saúde` | Ministério da Saúde (Órgão superior) |
| Educação | `Educação` | Ministério da Educação (Órgão superior) |
| Transportes | `Transportes` | Ministério dos Transportes (Órgão superior) |
| Cidades | `Cidades` | Ministério das Cidades (Órgão superior) |
| Integração | `Integração` | Ministério da Integração e do Desenvolvimento Regional (Órgão superior) |
| Portos | `Portos` | Ministério de Portos e Aeroportos (Órgão superior) |

Para trocar de órgão, use **Limpar filtros** (ou remova o órgão anterior)
antes de adicionar o próximo; senão a consulta soma os dois.

Se a Visualização gráfica não mostrar o valor de cada mês, anote isso na
coluna "Observações". Esse desvio é um dado do experimento, não um erro
seu. (Conferi que o bloco e as opções existem; não gerei o gráfico
filtrado, então "Valor apresentado" pode ter nomes ligeiramente
diferentes.)

**T3: favorecidos**

1. Abra https://portaldatransparencia.gov.br/despesas/recursos-recebidos
   (tela "Recebimento de Recursos por Favorecido").
2. Em **Período**, **Início** `03/2026` e **Fim** `08/2026`, clique em
   **Adicionar**. Em **Órgão**, digite o nome (tabela acima), espere a
   lista, escolha a linha **(Órgão superior)** e clique em **Adicionar**.
   (Nesta tela eu conferi o filtro, mas não testei a lista de órgãos;
   se vier diferente, anote.)
3. Clique no título da coluna **Valor Recebido** para ordenar do maior para
   o menor.
4. A tabela mostra uma linha por mês e favorecido. Some, na planilha, os
   valores do mesmo favorecido nos 6 meses e ordene.
5. Há opção "Visualização gráfica" no pé da tabela; pode usá-la se ajudar.

Atenção: as 10/20/30 linhas por página limitam a visão; anote quantas
páginas precisou percorrer.

---

## 4. Rodada 2 (com o RadarGov)

Faça uma pausa antes (nem que seja um café) e use a **variante B**.

1. Abra o relatório no Power BI Desktop (`RadarGov_Dashboard.pbix`).
2. Confira "Dados atualizados em" e anote.
3. **T1:** página "Visão Operacional" ou "Visão Executiva", segmentações
   de mês e órgão.
4. **T2:** matriz "Variação Mensal %" (Visão Operacional).
5. **T3:** gráfico "Total Recebido (favorecidos) por favorecido"
   (Visão Operacional, filtrar pelo órgão).
6. **T4:** gráfico de barras com a participação (dica de ferramenta
   "Participação na Área %") na Visão Executiva.

Cronometre da mesma forma e use o mesmo limite de 20 min.

---

## 5. Conferência (sem cronômetro)

1. Compare as respostas da Rodada 1 (Portal) com o que o dashboard mostra
   para as mesmas perguntas A. Diferenças pequenas podem vir de revisões
   da fonte; diferenças grandes são um defeito a investigar.
2. Repita no Portal, sem pressa, a **T1 variante B** (Educação, jul/2026) e
   compare com o dashboard. Isso cumpre o item "repetir a reconciliação
   para outro órgão/mês" que ficou sugerido em `RECONCILIACAO.md`.

---

## 6. Ficha de registro

### Rodada 1: Portal (variante A)

| Tarefa | Tempo (mm:ss) | Concluiu? | Resposta | Observações (o que travou, quantas consultas, reaproveitei de...) |
|---|---|---|---|---|
| T1 | | | | |
| T2 | | | | |
| T3 | | | | |
| T4 | | | | |
| **Total** | | | | |

### Rodada 2: RadarGov (variante B)

| Tarefa | Tempo (mm:ss) | Concluiu? | Resposta | Observações |
|---|---|---|---|---|
| T1 | | | | |
| T2 | | | | |
| T3 | | | | |
| T4 | | | | |
| **Total** | | | | |

Redução percentual = (tempo da Rodada 1 − tempo da Rodada 2) / tempo da
Rodada 1. Meta da H1: **≥ 50%**.

---

## 7. Satisfação (H4): autoavaliação na persona Rafael Andrade

Notas de 0 (péssimo) a 10 (excelente), respondidas logo após a Rodada 2:

| # | Pergunta | Nota |
|---|---|---|
| 1 | Foi fácil encontrar a informação que eu precisava? | |
| 2 | Os gráficos e tabelas são claros? | |
| 3 | Confio nos números apresentados? | |
| 4 | A sinalização de despesas atípicas ajuda a decidir onde olhar? | |
| 5 | Eu usaria o dashboard no lugar de consultar o Portal/planilhas? | |

Nota média = soma / 5. Comentário livre (1 a 3 linhas): ______________

---

## 8. Defeitos e melhorias encontrados

| # | O que aconteceu | Onde (página/visual) | Gravidade (alta/média/baixa) | Corrigir agora ou v2? |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

Itens já conhecidos para entrar aqui: formato "bi" nas tabelas de detalhe;
Publicar na Web ainda não confirmado; busca por texto no filtro de
favorecido não disponível.

---

## 9. Limitações (devem constar no relatório)

- **n = 1**, executado pelo próprio autor: é um teste de viabilidade, não
  uma validação estatística com usuários reais.
- **Viés a favor da H1 nos dois lados:** quem executa a Rodada 1 é iniciante
  no Portal (o tempo manual de um analista experiente seria menor) e conhece
  o dashboard por tê-lo construído (o tempo com o RadarGov também é menor
  do que seria para um usuário novo). O resultado deve ser lido como
  indicativo.
- **Satisfação é autoavaliação**, não pesquisa com a equipe da CIMG.
- A fonte revisa valores; as respostas dependem da data de atualização
  registrada no item 1.

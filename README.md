# RadarGov - MVP (pipeline de dados)

Monitoramento de despesas diretas da Uniao a partir do Portal da Transparencia,
para o Projeto Final de Curso (MBA IBMEC). Este repositorio cobre a **Sprint 1 -
Coleta e Engenharia de Dados**.

```
config.py                      -> configuracoes (o unico arquivo que voce edita)
de_para_orgao_area.csv         -> mapeamento orgao -> area de interesse
DICIONARIO_DE_DADOS.md         -> origem e significado dos campos
requirements.txt               -> bibliotecas Python
src/coleta.py                  -> baixa e consolida a base bruta
src/qualidade.py               -> valida a base e gera o relatorio de qualidade
dados/entrada/                 -> arquivos mensais baixados
dados/bruto/despesas_bruto.parquet   -> base consolidada (saida)
dados/tratado/relatorio_qualidade.md -> relatorio de qualidade (saida)
.github/workflows/pipeline.yml -> execucao automatica semanal (GitHub Actions)
```

---

## Parte A - Rodar no seu computador (uma vez, para validar)

### 1. Instalar o Python
- Baixe em https://www.python.org/downloads/ (versao 3.11 ou mais nova).
- No instalador, **marque "Add python.exe to PATH"** antes de clicar em Install.

### 2. Abrir o terminal na pasta do projeto
- Abra a pasta `radargov-mvp` no Explorador de Arquivos.
- Clique na barra de endereco, digite `cmd` e tecle Enter (abre o Prompt de Comando ja na pasta).

### 3. Instalar as bibliotecas
```
pip install -r requirements.txt
```

### 4. Rodar a coleta
```
python src/coleta.py
```
O script baixa um arquivo por mes, classifica cada orgao em uma area usando a
tabela `de_para_orgao_area.csv` (pelo **codigo do orgao superior**) e grava a
base em `dados/bruto/despesas_bruto.parquet`.

Na primeira execucao ele tambem **imprime o nome real das colunas** e uma lista
de **orgaos ainda sem classificacao**, ordenada por valor. Se algum orgao dessa
lista for de saude, educacao ou infraestrutura, adicione uma linha ao
`de_para_orgao_area.csv` no formato `codigo;nome;area` e rode de novo.

Se os nomes de coluna em `config.py` (`COL_COD_ORGAO`, `COL_ORGAO`,
`COL_FUNCAO`, `COL_VALOR`) nao baterem com os impressos, ajuste e rode de novo.

Se o download automatico falhar, baixe os arquivos manualmente em
https://portaldatransparencia.gov.br/download-de-dados/despesas-execucao
e salve-os na pasta `dados/entrada/`. O nome do arquivo deve conter o mes no
formato `AAAAMM` (ex.: `202603_...`). Depois rode `python src/coleta.py` de novo.

### 5. Rodar a validacao de qualidade
```
python src/qualidade.py
```
Isso gera `dados/tratado/relatorio_qualidade.md`.

### 6. Conferir a base
No mesmo terminal:
```
python -c "import pandas as pd; d=pd.read_parquet('dados/bruto/despesas_bruto.parquet'); print(d.shape); print(d.head()); print(d.dtypes)"
```

---

## Parte B - Publicar no GitHub e ligar a automacao

### 1. Criar conta e repositorio
- Crie uma conta em https://github.com (se ainda nao tiver).
- Clique em **New** (novo repositorio). De um nome (ex.: `radargov-mvp`),
  deixe **Private** ou **Public**, e clique em **Create repository**.

### 2. Enviar os arquivos (sem usar Git)
- Na pagina do repositorio recem-criado, clique em **Add file > Upload files**.
- Arraste **todo o conteudo** da pasta `radargov-mvp` (nao a pasta em si).
- Escreva uma mensagem ("primeira versao") e clique em **Commit changes**.

> A pasta `.github` e importante - confirme que ela subiu (o GitHub as vezes
> esconde pastas que comecam com ponto no Explorador do Windows; se nao
> aparecer, ative "Itens ocultos" na aba Exibir).

### 3. Dar permissao de escrita ao robo do Actions
- No repositorio: **Settings > Actions > General**.
- Em **Workflow permissions**, marque **Read and write permissions** e salve.
  (Sem isso, o passo que faz commit da base atualizada falha.)

### 4. Rodar o pipeline manualmente
- Aba **Actions > RadarGov - pipeline de ingestao > Run workflow**.
- Acompanhe a execucao. Ao terminar com o check verde, a base atualizada
  aparece em `dados/bruto/` no repositorio.

A partir dai o pipeline roda sozinho **toda segunda-feira**.

---

## Evidencias para a Sprint 1 (secao 4.1.1 do relatorio)

Tire print de:

1. A pagina do **repositorio no GitHub** (lista de arquivos e de commits).
2. Uma **resposta bem-sucedida** da fonte de dados (o resumo impresso pelo
   `coleta.py`, ou a tela de download do Portal).
3. A **base bruta**: saida do comando do passo A.6 (`shape`, `head`, `dtypes`).
4. A **tabela de-para** preenchida (`de_para_orgao_area.csv`), no formato `codigo;nome;area`.
5. O **relatorio de qualidade** (`dados/tratado/relatorio_qualidade.md`).
6. Um **run verde do GitHub Actions** (aba Actions, com o log aberto).
7. Trechos de codigo: `config.py`, `src/coleta.py`, `.github/workflows/pipeline.yml`.

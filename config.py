# -*- coding: utf-8 -*-
"""
Configuracoes do pipeline RadarGov.
Ajuste os valores abaixo conforme a necessidade do projeto.
Este e o unico arquivo que voce normalmente precisa editar.
"""

# ----------------------------------------------------------------------
# 1. JANELA DE DADOS
# ----------------------------------------------------------------------
# Quantos meses para tras, contados a partir do mes anterior ao atual.
# Comece com 6 para validar o pipeline; depois amplie para 24.
MESES_JANELA = 6

# ----------------------------------------------------------------------
# 2. AREAS DE INTERESSE DO MANDATO
# ----------------------------------------------------------------------
AREAS = ["saude", "educacao", "infraestrutura"]

# ----------------------------------------------------------------------
# 3. FONTE DE DADOS - arquivos mensais de "Execucao da Despesa"
#    Pagina de download:
#    https://portaldatransparencia.gov.br/download-de-dados/despesas-execucao
#
#    Baixe UM arquivo manualmente pela pagina, abra o ZIP e confira:
#      - o nome exato das colunas (ajuste na secao 4)
#      - o separador, a codificacao e o separador decimal (secao 5)
#    O padrao de URL abaixo pode mudar. Se o download automatico falhar,
#    o script explica como colocar os arquivos manualmente em dados/entrada/.
# ----------------------------------------------------------------------
URL_DOWNLOAD = "https://portaldatransparencia.gov.br/download-de-dados/despesas-execucao/{aaaamm}"

# ----------------------------------------------------------------------
# 4. NOMES DAS COLUNAS NO CSV
#    Rode "python src/coleta.py" uma vez: ele imprime as colunas reais
#    do primeiro arquivo. Copie os nomes exatos para ca.
# ----------------------------------------------------------------------
COL_COD_ORGAO = "Código Órgão Superior"   # chave de classificacao (numero estavel)
COL_ORGAO  = "Nome Órgão Superior"        # nome do orgao (apenas para leitura; o Portal corta em 43 caracteres)
COL_FUNCAO = "Nome Função"                # funcao de governo (saude, educacao, etc.)
COL_VALOR  = "Valor Pago (R$)"            # valor efetivamente desembolsado no mes
# Alternativas presentes no arquivo, caso queira trocar a medida de gasto:
#   "Valor Empenhado (R$)"  -> verba comprometida
#   "Valor Liquidado (R$)"  -> servico/produto entregue e conferido

# ----------------------------------------------------------------------
# 5. FORMATO DO ARQUIVO CSV
# ----------------------------------------------------------------------
CSV_SEP = ";"
CSV_ENCODING = "latin-1"     # arquivos antigos do Portal costumam ser latin-1; se der erro de acento, troque para "utf-8"
CSV_DECIMAL = ","

# ----------------------------------------------------------------------
# 6. CAMINHOS (nao precisa mexer)
# ----------------------------------------------------------------------
import pathlib
RAIZ = pathlib.Path(__file__).resolve().parent
DIR_ENTRADA = RAIZ / "dados" / "entrada"     # ZIPs/CSVs baixados
DIR_BRUTO   = RAIZ / "dados" / "bruto"       # base consolidada (saida da coleta)
DIR_TRATADO = RAIZ / "dados" / "tratado"     # relatorio de qualidade
ARQ_DE_PARA = RAIZ / "de_para_orgao_area.csv"
ARQ_BASE_BRUTA = DIR_BRUTO / "despesas_bruto.parquet"
ARQ_RELATORIO  = DIR_TRATADO / "relatorio_qualidade.md"

# ----------------------------------------------------------------------
# 7. PILOTO - RANKING DE FAVORECIDOS (Sprint 2, escopo restrito)
#    Testa se e viavel identificar os maiores favorecidos de um orgao
#    em um mes, via API do Portal (endpoint paginado, exige chave).
#    Precisa de um arquivo .env na raiz do projeto com:
#      PORTAL_API_KEY=sua_chave_aqui
#    (veja .env.example). O .env nunca e enviado ao GitHub.
# ----------------------------------------------------------------------
FAV_ORGAO_SUPERIOR = "68000"   # codigo SIAFI do orgao piloto (68000 = Ministerio de Portos e Aeroportos)
FAV_MES_ANO = "08/2026"        # mes piloto, formato MM/AAAA
FAV_MAX_PAGINAS = 500          # trava de seguranca contra loop infinito

ARQ_FAV_BRUTO   = DIR_BRUTO   / "favorecidos_piloto_bruto.parquet"
ARQ_FAV_RANKING = DIR_TRATADO / "ranking_favorecidos_piloto.md"

# ----------------------------------------------------------------------
# 8. FAVORECIDOS POR AREA (producao)
#    Cobre TODOS os orgaos de uma area (de_para_orgao_area.csv), na
#    mesma janela de MESES_JANELA. Testado e viavel apenas para
#    "infraestrutura" - saude e educacao tem volume muito maior por mes
#    (medido: saude ~2.500-3.000 paginas; educacao ~16.000-32.000
#    paginas; infraestrutura ~600-650 paginas) e ficam fora do MVP.
#    Ver DICIONARIO_DE_DADOS.md para o detalhe da medicao.
# ----------------------------------------------------------------------
FAV_AREA = "infraestrutura"
FAV_MAX_PAGINAS_POR_COMBO = 800   # trava de seguranca por (orgao, mes)

ARQ_FAV_INFRA_BRUTO   = DIR_BRUTO   / "favorecidos_infraestrutura_bruto.parquet"
ARQ_FAV_INFRA_RANKING = DIR_TRATADO / "ranking_favorecidos_infraestrutura.md"

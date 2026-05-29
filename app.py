import streamlit as st
import pandas as pd
import json
import os
import pytz
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Configuração da página para um visual limpo e moderno
st.set_page_config(page_title="Gestão Financeira Mensal", page_icon="💰", layout="centered")

# Nome do arquivo onde os dados serão salvos localmente
ARQUIVO_DADOS = "dados_mes.json"

# --- DEFINIÇÃO DE FUSO HORÁRIO ---
try:
    fuso_br = pytz.timezone('America/Sao_Paulo')
    agora_br = datetime.now(fuso_br).date()
except Exception:
    agora_br = datetime.now().date()

# --- CONEXÃO COM GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Erro na conexão com o Google Sheets: {e}")

# --- FUNÇÕES DE PERSISTÊNCIA DE DADOS LOCAL ---
def carregar_dados():
    """Carrega os dados salvos do último uso. Se não existirem, usa os padrões iniciais."""
    valores_padrao = {
        "adiantamento": 2082.22,
        "salario_oficial": 3152.25,
        "porcentagem_guardar": 10,
        "compras_mes": 750.00,
        "combustivel_carro": 250.00,
        "combustivel_moto": 120.00,
        "financiamento": 1400.00,
        "condominio": 400.00,
        "iptu": 100.00,
        "seguro_residencial": 30.00,
        "claro_tv_internet": 150.00,
        "luz": 80.00,
        "celular": 40.00
    }
    
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                dados_salvos = json.load(f)
                for chave, valor in valores_padrao.items():
                    dados_salvos.setdefault(chave, valor)
                return dados_salvos
        except Exception:
            return valores_padrao
    return valores_padrao

# Função para buscar o histórico de gastos reais na planilha Google Sheets
def carregar_gastos_reais():
    try:
        df = conn.read(worksheet="Gastos", ttl=0)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        df = df.dropna(how="all")
        return df
    except Exception:
        return pd.DataFrame(columns=["Data", "Descricao", "Categoria", "Valor"])

# Inicializa ou carrega os dados no estado da sessão do Streamlit
if "dados" not in st.session_state:
    st.session_state.dados = carregar_dados()

# Estilização customizada básica para os cartões de métricas
st.markdown("""
    <style>
    .metric-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-title { font-size: 14px; color: #555; font-weight: bold; }
    .metric-value { font-size: 22px; color: #1e3d59; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("💰 Gestão de Salário & Planejamento Mensal")
st.write("Os campos abaixo exibem os valores salvos do seu último acesso. Altere-os e clique em salvar no final da página.")

st.divider()

# --- SEÇÃO 1: ENTRADAS DE RENDA ---
st.subheader("📥 Recebimentos do Mês")

col1, col2 = st.columns(2)
with col1:
    adiantamento = st.number_input("Adiantamento (Dia 20) - R$", min_value=0.0, value=st.session_state.dados["adiantamento"], step=100.0, format="%.2f")
with col2:
    salario_oficial = st.number_input("Pagamento Oficial (Dia 05) - R$", min_value=0.0, value=st.session_state.dados["salario_oficial"], step=100.0, format="%.2f")

renda_total = adiantamento + salario_oficial

porcentagem_guardar = st.slider("Porcentagem que deseja guardar este mês:", min_value=0, max_value=100, value=int(st.session_state.dados["porcentagem_guardar"]), step=5)

st.divider()

# --- SEÇÃO 2: GASTOS VARIÁVEIS (MERCADO E COMBUSTÍVEL) ---
st.subheader("🚗 Gastos Variáveis do Mês")
st.write("Ajuste a previsão de despesas maleáveis para este mês:")

gv_col1, gv_col2 = st.columns(2)

with gv_col1:
    compras_mes = st.number_input("Supermercado / Alimentação - R$", min_value=0.0, value=st.session_state.dados["compras_mes"], step=50.0, format="%.2f")
    combustivel_carro = st.number_input("Combustível: Carro - R$", min_value=0.0, value=st.session_state.dados["combustivel_carro"], step=50.0, format="%.2f")

with gv_col2:
    combustivel_moto = st.number_input("Combustível: Moto - R$", min_value=0.0, value=st.session_state.dados["combustivel_moto"], step=20.0, format="%.2f")

gastos_variaveis_total = compras_mes + combustivel_carro + combustivel_moto

st.divider()

# --- SEÇÃO 3: DETALHAMENTO DE CONTAS FIXAS ---
st.subheader("📌 Detalhamento das Contas Fixas")
st.write("Ajuste os valores reais de cada boleto de moradia e consumo:")

cf_col1, cf_col2 = st.columns(2)

with cf_col1:
    financiamento = st.number_input("Financiamento do Ap - R$", min_value=

import streamlit as st
import pandas as pd
import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuração da página
st.set_page_config(page_title="Gestão Financeira Mensal", page_icon="💰", layout="centered")

ARQUIVO_DADOS = "dados_mes.json"

# --- FUNÇÃO: SALVAR NO GOOGLE SHEETS ---
def salvar_no_sheets(dados_extra):
    # O dict abaixo deve corresponder à estrutura do seu st.secrets
    # Exemplo: st.secrets["gcp_service_account"]
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    # IMPORTANTE: Certifique-se de configurar os secrets no Streamlit Cloud
    creds_dict = dict(st.secrets["gcp_service_account"]) 
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    spreadsheet = client.open_by_key("1X74m1kSZIx_eLdGTb8ZOf4RNK-PrFWFlmdx4gtgig9Q")
    sheet = spreadsheet.worksheet("Gastos")
    sheet.append_row([pd.Timestamp.now().strftime("%d/%m/%Y"), dados_extra['desc'], "Extra", dados_extra['valor']])

# --- CARREGAMENTO INICIAL ---
def carregar_dados():
    padrao = {
        "adiantamento": 2082.22, "salario_oficial": 3152.25, "porcentagem_guardar": 10,
        "compras_mes": 750.00, "combustivel_carro": 250.00, "combustivel_moto": 120.00,
        "financiamento": 1400.00, "condominio": 400.00, "iptu": 100.00,
        "seguro_residencial": 30.00, "claro_tv_internet": 150.00, "luz": 80.00, "celular": 40.00
    }
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return padrao
    return padrao

if "dados" not in st.session_state:
    st.session_state.dados = carregar_dados()
if "gastos_avulsos" not in st.session_state:
    st.session_state.gastos_avulsos = []

st.title("💰 Gestão de Salário & Planejamento Mensal")

# --- INPUTS ---
col1, col2 = st.columns(2)
with col1: adiantamento = st.number_input("Adiantamento (Dia 20) - R$", value=st.session_state.dados.get("adiantamento", 0.0), step=100.0)
with col2: salario_oficial = st.number_input("Pagamento Oficial (Dia 05) - R$", value=st.session_state.dados.get("salario_oficial", 0.0), step=100.0)
porcentagem_guardar = st.slider("Porcentagem a guardar:", 0, 100, int(st.session_state.dados.get("porcentagem_guardar", 10)))

# --- GASTOS FIXOS/VARIÁVEIS ---
compras_mes = st.number_input("Supermercado - R$", value=st.session_state.dados.get("compras_mes", 0.0), step=50.0)
combustivel_carro = st.number_input("Combustível Carro - R$", value=st.session_state.dados.get("combustivel_carro", 0.0), step=50.0)
combustivel_moto = st.number_input("Combustível Moto - R$", value=st.session_state.dados.get("combustivel_moto", 0.0), step=20.0)
financiamento = st.number_input("Financiamento - R$", value=st.session_state.dados.get("financiamento", 0.0), step=50.0)
condominio = st.number_input("Condomínio - R$", value=st.session_state.dados.get("condominio", 0.0), step=20.0)
iptu = st.number_input("IPTU - R$", value=st.session_state.dados.get("iptu", 0.0), step=10.0)
seguro_residencial = st.number_input("Seguro Residencial - R$", value=st.session_state.dados.get("seguro_residencial", 0.0), step=5.0)
claro_tv_internet = st.number_input("Claro - R$", value=st.session_state.dados.get("claro_tv_internet", 0.0), step=10.0)
luz = st.number_input("Luz - R$", value=st.session_state.dados.get("luz", 0.0), step=10.0)
celular = st.number_input("Celular - R$", value=st.session_state.dados.get("celular", 0.0), step=5.0)

# --- GASTOS AVULSOS ---
st.divider()
st.subheader("📝 Adicionar Gastos Avulsos")
c1, c2, c3 = st.columns([2, 1, 1])
with c1: desc_extra = st.text_input("Descrição")
with c2: valor_extra = st.number_input("Valor (R$)", min_value=0.0, step=1.0)
with c3:
    st.write("###")
    if st.button("Adicionar"):
        if desc_extra and valor_extra > 0:
            novo_gasto = {"desc": desc_extra, "valor": valor_extra}
            st.session_state.gastos_avulsos.append(novo_gasto)
            try:
                salvar_no_sheets(novo_gasto)
                st.success("Adicionado à planilha!")
            except Exception as e:
                st.error(f"Erro ao salvar na planilha: {e}")
            st.rerun()

# --- CÁLCULOS E PROJEÇÕES ---
renda_total = adiantamento + salario_oficial
total_extras = sum(item['valor'] for item in st.session_state.gastos_avulsos)
contas_fixas_total = financiamento + condominio + iptu + seguro_residencial + claro_tv_internet + luz + celular
gastos_variaveis_total = compras_mes + combustivel_carro + combustivel_moto
valor_guardar = renda_total * (porcentagem_guardar / 100)
saldo_livre = renda_total - valor_guardar - contas_fixas_total - gastos_variaveis_total - total_extras

# --- QUADROS AZUIS ---
if renda_total > 0:
    p_adiantamento = adiantamento / renda_total
    p_oficial = salario_oficial / renda_total
    st.subheader("📅 O que fazer quando o dinheiro cair?")
    c_d20, c_d05 = st.columns(2)
    with c_d20: st.info(f"### 🏦 Dia 20\n* Poupar: R$ {adiantamento*(porcentagem_guardar/100):,.2f}\n* Fixas: R$ {contas_fixas_total*p_adiantamento:,.2f}")
    with c_d05: st.info(f"### 🏢 Dia 05\n* Poupar: R$ {salario_oficial*(porcentagem_guardar/100):,.2f}\n* Fixas: R$ {contas_fixas_total*p_oficial:,.2f}")

st.success(f"### Saldo Livre: R$ {saldo_livre:,.2f}")

# --- SALVAR PADRÕES ---
if st.button("Salvar Tudo como Padrão", type="primary"):
    novo_json = {
        "adiantamento": adiantamento, "salario_oficial": salario_oficial, "porcentagem_guardar": porcentagem_guardar,
        "compras_mes": compras_mes, "combustivel_carro": combustivel_carro, "combustivel_moto": combustivel_moto,
        "financiamento": financiamento, "condominio": condominio, "iptu": iptu,
        "seguro_residencial": seguro_residencial, "claro_tv_internet": claro_tv_internet, "luz": luz, "celular": celular
    }
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(novo_json, f, ensure_ascii=False, indent=4)
    st.success("Dados salvos!")

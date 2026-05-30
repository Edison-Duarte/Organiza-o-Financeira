import streamlit as st
import pandas as pd
import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="Gestão Financeira", page_icon="💰", layout="centered")

ARQUIVO_DADOS = "dados_mes.json"

# --- FUNÇÃO DE ESCRITA NO SHEETS ---
def salvar_no_sheets(desc, valor):
    # Tenta ler as credenciais dos secrets do Streamlit
    creds_dict = dict(st.secrets["gcp_service_account"])
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    # ID da sua planilha "Controle_Financeiro"
    spreadsheet = client.open_by_key("1X74m1kSZIx_eLdGTb8ZOf4RNK-PrFWFlmdx4gtgig9Q")
    sheet = spreadsheet.worksheet("Gastos")
    sheet.append_row([pd.Timestamp.now().strftime("%d/%m/%Y"), desc, "Extra", valor])

# --- CARREGAMENTO ---
def carregar_dados():
    padrao = {"adiantamento": 2082.22, "salario_oficial": 3152.25, "porcentagem_guardar": 10,
              "compras_mes": 750.00, "combustivel_carro": 250.00, "combustivel_moto": 120.00,
              "financiamento": 1400.00, "condominio": 400.00, "iptu": 100.00,
              "seguro_residencial": 30.00, "claro_tv_internet": 150.00, "luz": 80.00, "celular": 40.00}
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return padrao
    return padrao

if "dados" not in st.session_state: st.session_state.dados = carregar_dados()
if "gastos_avulsos" not in st.session_state: st.session_state.gastos_avulsos = []

st.title("💰 Gestão Financeira")

# --- INPUTS (simplificados para o exemplo) ---
adiantamento = st.number_input("Adiantamento", value=st.session_state.dados.get("adiantamento", 0.0))
salario_oficial = st.number_input("Salário Oficial", value=st.session_state.dados.get("salario_oficial", 0.0))

# --- GASTOS AVULSOS ---
st.subheader("📝 Adicionar Gastos Avulsos")
col1, col2, col3 = st.columns([2, 1, 1])
with col1: desc = st.text_input("Descrição")
with col2: val = st.number_input("Valor", min_value=0.0)
with col3:
    st.write("###")
    if st.button("Adicionar"):
        if desc and val > 0:
            try:
                salvar_no_sheets(desc, val)
                st.session_state.gastos_avulsos.append({"desc": desc, "valor": val})
                st.success("Salvo na planilha!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro na planilha: {e}")

# --- RESULTADOS ---
total_extras = sum(item['valor'] for item in st.session_state.gastos_avulsos)
st.write(f"### Total Extras: R$ {total_extras:,.2f}")

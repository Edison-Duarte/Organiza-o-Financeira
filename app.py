import streamlit as st
import pandas as pd
import json
import os

# Configuração da página para um visual limpo e moderno
st.set_page_config(page_title="Gestão Financeira Mensal", page_icon="💰", layout="centered")

# Nome do arquivo onde os dados serão salvos localmente
ARQUIVO_DADOS = "dados_mes.json"

# --- FUNÇÕES DE PERSISTÊNCIA DE DADOS ---
def carregar_dados():
    """Carrega os dados salvos do último uso. Se não existirem, usa os padrões iniciais."""
    valores_padrao = {
        "adiantamento": 2082.22,
        "salario_oficial": 3152.25,
        "porcentagem_guardar": 10,
        "compras_mes": 750.00,
        "combustivel_carro": 250.00,
        "combustivel_moto": 120.00,
        "cartao_credito": 500.00,  # <-- ADICIONADO
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

# --- SEÇÃO 2: GASTOS VARIÁVEIS ---
st.subheader("🚗 Gastos Variáveis do Mês")
st.write("Ajuste a previsão de despesas maleáveis para este mês:")

gv_col1, gv_col2 = st.columns(2)

with gv_col1:
    compras_mes = st.number_input("Supermercado / Alimentação - R$", min_value=0.0, value=st.session_state.dados["compras_mes"], step=50.0, format="%.2f")
    combustivel_carro = st.number_input("Combustível: Carro - R$", min_value=0.0, value=st.session_state.dados["combustivel_carro"], step=50.0, format="%.2f")

with gv_col2:
    combustivel_moto = st.number_input("Combustível: Moto - R$", min_value=0.0, value=st.session_state.dados["combustivel_moto"], step=20.0, format="%.2f")
    cartao_credito = st.number_input("Cartão de Crédito - R$", min_value=0.0, value=st.session_state.dados["cartao_credito"], step=50.0, format="%.2f") # <-- ADICIONADO

gastos_variaveis_total = compras_mes + combustivel_carro + combustivel_moto + cartao_credito # <-- ATUALIZADO

st.divider()

# --- SEÇÃO 3: DETALHAMENTO DE CONTAS FIXAS ---
st.subheader("📌 Detalhamento das Contas Fixas")
st.write("Ajuste os valores reais de cada boleto de moradia e consumo:")

cf_col1, cf_col2 = st.columns(2)

with cf_col1:
    financiamento = st.number_input("Financiamento do Ap - R$", min_value=0.0, value=st.session_state.dados["financiamento"], step=50.0, format="%.2f")
    condominio = st.number_input("Condomínio - R$", min_value=0.0, value=st.session_state.dados["condominio"], step=20.0, format="%.2f")
    iptu = st.number_input("IPTU - R$", min_value=0.0, value=st.session_state.dados["iptu"], step=10.0, format="%.2f")
    seguro_residencial = st.number_input("Seguro Residencial - R$", min_value=0.0, value=st.session_state.dados["seguro_residencial"], step=5.0, format="%.2f")

with cf_col2:
    claro_tv_internet = st.number_input("Claro (Internet/TV) - R$", min_value=0.0, value=st.session_state.dados["claro_tv_internet"], step=10.0, format="%.2f")
    luz = st.number_input("Conta de Luz - R$", min_value=0.0, value=st.session_state.dados["luz"], step=10.0, format="%.2f")
    celular = st.number_input("Conta de Celular - R$", min_value=0.0, value=st.session_state.dados["celular"], step=5.0, format="%.2f")

contas_fixas_total = financiamento + condominio + iptu + seguro_residencial + claro_tv_internet + luz + celular

# --- CÁLCULOS FINANCEIROS ---
valor_guardar = renda_total * (porcentagem_guardar / 100)

if renda_total > 0:
    saldo_livre = renda_total - valor_guardar - contas_fixas_total - gastos_variaveis_total
    # ... (Restante do cálculo permanece igual)
    p_adiantamento = adiantamento / renda_total
    p_oficial = salario_oficial / renda_total
    
    poupança_dia20 = adiantamento * (porcentagem_guardar / 100)
    fixas_dia20 = contas_fixas_total * p_adiantamento
    total_reter_dia20 = poupança_dia20 + fixas_dia20
    porcentagem_reter_dia20 = (total_reter_dia20 / adiantamento) * 100 if adiantamento > 0 else 0
    p_reter_d20_do_total = (total_reter_dia20 / renda_total) * 100
    
    poupança_dia05 = salario_oficial * (porcentagem_guardar / 100)
    fixas_dia05 = contas_fixas_total * p_oficial
    total_reter_dia05 = poupança_dia05 + fixas_dia05
    porcentagem_reter_dia05 = (total_reter_dia05 / salario_oficial) * 100 if salario_oficial > 0 else 0
    p_reter_d05_do_total = (total_reter_dia05 / renda_total) * 100
else:
    saldo_livre = 0.0

# --- SEÇÃO 4: PAINEL DE RESULTADOS ---
st.subheader("📊 Resumo Financeiro")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Renda Total</div><div class="metric-value">R$ {renda_total:,.2f}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Poupança Total</div><div class="metric-value" style="color: #2e7d32;">R$ {valor_guardar:,.2f}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Contas Fixas</div><div class="metric-value" style="color: #c62828;">R$ {contas_fixas_total:,.2f}</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Variáveis Previstas</div><div class="metric-value" style="color: #f57c00;">R$ {gastos_variaveis_total:,.2f}</div></div>', unsafe_allow_html=True)

# ... (Exibição dos resultados e salvamento mantidos)
# [Nota: Certifique-se de incluir 'cartao_credito' no dicionário 'novos_dados' ao salvar abaixo]

# --- SEÇÃO DE PERSISTÊNCIA (SALVAR DADOS) ---
st.divider()
st.subheader("💾 Gerenciamento de Histórico")

if st.button("Salvar Valores Atuais como Padrão", type="primary", use_container_width=True):
    novos_dados = {
        "adiantamento": adiantamento,
        "salario_oficial": salario_oficial,
        "porcentagem_guardar": porcentagem_guardar,
        "compras_mes": compras_mes,
        "combustivel_carro": combustivel_carro,
        "combustivel_moto": combustivel_moto,
        "cartao_credito": cartao_credito,
        "financiamento": financiamento,
        "condominio": condominio,
        "iptu": iptu,
        "seguro_residencial": seguro_residencial,
        "claro_tv_internet": claro_tv_internet,
        "luz": luz,
        "celular": celular
    }
    try:
        with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
            json.dump(novos_dados, f, ensure_ascii=False, indent=4)
        st.session_state.dados = novos_dados
        st.success("🎉 Valores salvos com sucesso!")
    except Exception as e:
        st.error(f"Erro ao salvar os dados localmente: {e}")

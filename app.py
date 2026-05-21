import streamlit as st
import pandas as pd

# Configuração da página para um visual limpo e moderno
st.set_page_config(page_title="Gestão Financeira Mensal", page_icon="💰", layout="centered")

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
st.write("Insira seus recebimentos e detalhe suas contas para organizar o mês.")

st.divider()

# --- SEÇÃO 1: ENTRADAS DE RENDA ---
st.subheader("📥 Recebimentos do Mês")

col1, col2 = st.columns(2)
with col1:
    adiantamento = st.number_input("Adiantamento (Dia 20) - R$", min_value=0.0, value=0.0, step=100.0, format="%.2f")
with col2:
    salario_oficial = st.number_input("Pagamento Oficial (Dia 05) - R$", min_value=0.0, value=0.0, step=100.0, format="%.2f")

# Cálculo da renda total
renda_total = adiantamento + salario_oficial

# Seletor da porcentagem para guardar
porcentagem_guardar = st.slider("Porcentagem que deseja guardar este mês:", min_value=0, max_value=100, value=10, step=5)

st.divider()

# --- SEÇÃO 2: DETALHAMENTO DE CONTAS FIXAS ---
st.subheader("📌 Detalhamento das Contas Fixas")
st.write("Ajuste os valores reais de cada conta para este mês:")

# Organizando as contas fixas em colunas para não ocupar muito espaço vertical
cf_col1, cf_col2 = st.columns(2)

with cf_col1:
    financiamento = st.number_input("Financiamento do Ap - R$", min_value=0.0, value=1400.00, step=50.0, format="%.2f")
    condominio = st.number_input("Condomínio - R$", min_value=0.0, value=400.00, step=20.0, format="%.2f")
    iptu = st.number_input("IPTU - R$", min_value=0.0, value=100.00, step=10.0, format="%.2f")
    seguro_residencial = st.number_input("Seguro Residencial - R$", min_value=0.0, value=30.00, step=5.0, format="%.2f")

with cf_col2:
    claro_tv_internet = st.number_input("Claro (Internet/TV) - R$", min_value=0.0, value=150.00, step=10.0, format="%.2f")
    luz = st.number_input("Conta de Luz - R$", min_value=0.0, value=80.00, step=10.0, format="%.2f")
    celular = st.number_input("Conta de Celular - R$", min_value=0.0, value=40.00, step=5.0, format="%.2f")

# Soma dinâmica de todas as contas fixas inseridas pelo usuário
contas_fixas_total = financiamento + condominio + iptu + seguro_residencial + claro_tv_internet + luz + celular

st.divider()

# --- CÁLCULOS FINANCEIROS ---
valor_guardar = renda_total * (porcentagem_guardar / 100)

# Garante que o saldo livre faça cálculos corretdos se houver renda
if renda_total > 0:
    saldo_livre = renda_total - valor_guardar - contas_fixas_total
else:
    saldo_livre = 0.0

# --- SEÇÃO 3: PAINEL DE RESULTADOS ---
st.subheader("📊 Resumo Financeiro")

# Layout de cartões (Cards)
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Renda Total</div><div class="metric-value">R$ {renda_total:,.2f}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Meta de Poupança ({porcentagem_guardar}%)</div><div class="metric-value" style="color: #2e7d32;">R$ {valor_guardar:,.2f}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Total Contas Fixas</div><div class="metric-value" style="color: #c62828;">R$ {contas_fixas_total:,.2f}</div></div>', unsafe_allow_html=True)

st.markdown("")

# Cartão de Destaque para o Saldo Livre (Apenas exibe se houver renda digitada)
if renda_total > 0:
    if saldo_livre >= 0:
        st.success(f"### 🎉 Saldo Livre para o Mês: **R$ {saldo_livre:,.2f}**")
        st.caption("Este é o valor disponível para mercado, lazer, gasolina, manutenção do carro/moto, despesas do apartamento, etc.")
    else:
        st.error(f"### ⚠️ Atenção! Orçamento estourado em: **R$ {abs(saldo_livre):,.2f}**")
        st.caption("A soma das contas fixas e da meta de poupança superou a sua renda este mês. Reduza os valores ou mude a porcentagem de poupança.")

    # --- TABELA DE DISTRIBUIÇÃO ---
    st.markdown("#### 📋 Visão Geral do Destino do Salário")
    
    p_poupança = (valor_guardar / renda_total) * 100
    p_fixas = (contas_fixas_total / renda_total) * 100
    p_livre = (max(0.0, saldo_livre) / renda_total) * 100

    df_distribuicao = pd.DataFrame({
        "Destino do Dinheiro": ["Poupança (Reservas)", "Contas Fixas Somadas", "Saldo Livre (Variáveis/Estilo de Vida)"],
        "Valor Total (R$)": [f"R$ {valor_guardar:,.2f}", f"R$ {contas_fixas_total:,.2f}", f"R$ {max(0.0, saldo_livre):,.2f}"],
        "Porcentagem do Salário": [f"{p_poupança:.1f}%", f"{p_fixas:.1f}%", f"{p_livre:.1f}%"]
    })
    
    st.dataframe(df_distribuicao, hide_index=True, use_container_width=True)

else:
    st.info("💡 Insira os valores de Adiantamento e Pagamento no topo da página para calcular o seu Saldo Livre.")

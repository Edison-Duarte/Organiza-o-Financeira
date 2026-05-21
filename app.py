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
st.write("Insira seus recebimentos, gerencie suas contas fixas e estime seus gastos variáveis.")

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

# --- SEÇÃO 2: GASTOS VARIÁVEIS (MERCADO E COMBUSTÍVEL) ---
st.subheader("🚗 Gastos Variáveis do Mês")
st.write("Ajuste a previsão de despesas maleáveis para este mês:")

gv_col1, gv_col2 = st.columns(2)

with gv_col1:
    compras_mes = st.number_input("Supermercado / Alimentação - R$", min_value=0.0, value=750.00, step=50.0, format="%.2f")
    combustivel_carro = st.number_input("Combustível: Carro - R$", min_value=0.0, value=250.00, step=50.0, format="%.2f")

with gv_col2:
    combustivel_moto = st.number_input("Combustível: Moto - R$", min_value=0.0, value=120.00, step=20.0, format="%.2f")

# Soma dinâmica de todas as variáveis informadas
gastos_variaveis_total = compras_mes + combustivel_carro + combustivel_moto

st.divider()

# --- SEÇÃO 3: DETALHAMENTO DE CONTAS FIXAS ---
st.subheader("📌 Detalhamento das Contas Fixas")
st.write("Ajuste os valores reais de cada boleto de moradia e consumo:")

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

# Soma dinâmica de todas as contas fixas
contas_fixas_total = financiamento + condominio + iptu + seguro_residencial + claro_tv_internet + luz + celular

st.divider()

# --- CÁLCULOS FINANCEIROS ---
valor_guardar = renda_total * (porcentagem_guardar / 100)

# O saldo livre deduz as fixas e as variáveis
if renda_total > 0:
    saldo_livre = renda_total - valor_guardar - contas_fixas_total - gastos_variaveis_total
    
    # Cálculos de Proporção para a sua necessidade de carimbo de saldo
    p_adiantamento = adiantamento / renda_total
    p_oficial = salario_oficial / renda_total
    
    # Provisão proporcional do Adiantamento (Dia 20)
    poupança_dia20 = adiantamento * (porcentagem_guardar / 100)
    fixas_dia20 = contas_fixas_total * p_adiantamento
    total_reter_dia20 = poupança_dia20 + fixas_dia20
    porcentagem_reter_dia20 = (total_reter_dia20 / adiantamento) * 100 if adiantamento > 0 else 0
    
    # Provisão proporcional do Pagamento Oficial (Dia 05)
    poupança_dia05 = salario_oficial * (porcentagem_guardar / 100)
    fixas_dia05 = contas_fixas_total * p_oficial
else:
    saldo_livre = 0.0
    porcentagem_reter_dia20 = 0.0
    total_reter_dia20 = 0.0
    poupança_dia20 = 0.0
    fixas_dia20 = 0.0

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

st.markdown("")

if renda_total > 0:
    if saldo_livre >= 0:
        st.success(f"### 🎉 Saldo Livre para Lazer: **R$ {saldo_livre:,.2f}**")
    else:
        st.error(f"### ⚠️ Atenção! Orçamento estourado em: **R$ {abs(saldo_livre):,.2f}**")

    # --- NOVA SEÇÃO INTERATIVA: PROGRAMAÇÃO DE RETENÇÃO POR DATA ---
    st.divider()
    st.subheader("📅 O que fazer quando o dinheiro cair?")
    
    col_d20, col_d05 = st.columns(2)
    
    with col_d20:
        st.info(f"### 🏦 Dia 20 (Adiantamento)\n"
                f"Você deve reter **{porcentagem_reter_dia20:.1f}%** deste valor.\n\n"
                f"*   **Poupar (Meta):** R$ {poupança_dia20:,.2f}\n"
                f"*   **Reservar para Contas:** R$ {fixas_dia20:,.2f}\n"
                f"**Total a reter/guardar:** R$ {total_reter_dia20:,.2f}")
                
    with col_d05:
        st.info(f"### 🏢 Dia 05 (Pagamento Oficial)\n"
                f"Retenha o restante proporcional para quitar o mês.\n\n"
                f"*   **Poupar (Meta):** R$ {poupança_dia05:,.2f}\n"
                f"*   **Separar para Contas:** R$ {fixas_dia05:,.2f}\n"
                f"**Junte com a reserva do dia 20 para pagar os boletos.**")

    # --- TABELA DE DISTRIBUIÇÃO ---
    st.markdown("#### 📋 Distribuição Geral do Orçamento")
    
    p_poupança = (valor_guardar / renda_total) * 100
    p_fixas = (contas_fixas_total / renda_total) * 100
    p_variaveis = (gastos_variaveis_total / renda_total) * 100
    p_livre = (max(0.0, saldo_livre) / renda_total) * 100

    df_distribuicao = pd.DataFrame({
        "Destino do Dinheiro": ["Poupança (Investimentos)", "Contas Fixas (Moradia/Consumo)", "Gastos Variáveis (Mercado/Combustíveis)", "Saldo Livre (Lazer/Hobbies)"],
        "Valor Total (R$)": [f"R$ {valor_guardar:,.2f}", f"R$ {contas_fixas_total:,.2f}", f"R$ {gastos_variaveis_total:,.2f}", f"R$ {max(0.0, saldo_livre):,.2f}"],
        "Porcentagem do Salário": [f"{p_poupança:.1f}%", f"{p_fixas:.1f}%", f"{p_variaveis:.1f}%", f"{p_livre:.1f}%"]
    })
    
    st.dataframe(df_distribuicao, hide_index=True, use_container_width=True)
else:
    st.info("💡 Insira os valores de Adiantamento e Pagamento no topo para recalcular todo o ecossistema financeiro.")

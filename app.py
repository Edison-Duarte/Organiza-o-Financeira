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
st.write("Insira os valores recebidos e planeje o mês de forma inteligente.")

st.divider()

# --- ENTRADAS DE DADOS ---
st.subheader("📥 Entradas do Mês")

col1, col2 = st.columns(2)
with col1:
    adiantamento = st.number_input("Adiantamento (Dia 20) - R$", min_value=0.0, value=0.0, step=100.0, format="%.2f")
with col2:
    salario_oficial = st.number_input("Pagamento Oficial (Dia 05) - R$", min_value=0.0, value=0.0, step=100.0, format="%.2f")

# Cálculo da renda total
renda_total = adiantamento + salario_oficial

# Seletor da porcentagem para guardar
porcentagem_guardar = st.slider("Porcentagem que deseja guardar este mês:", min_value=0, max_value=100, value=10, step=5)

# --- CÁLCULOS FINANCEIROS ---
valor_guardar = renda_total * (porcentagem_guardar / 100)
contas_fixas = 2200.00  # Média informada por você

# Garante que o saldo livre não faça cálculos errados se a renda for 0
if renda_total > 0:
    saldo_livre = renda_total - valor_guardar - contas_fixas
else:
    saldo_livre = 0.0

st.divider()

# --- PAINEL DE RESULTADOS ---
st.subheader("📊 Resumo Financeiro")

# Layout de cartões (Cards)
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Renda Total</div><div class="metric-value">R$ {renda_total:,.2f}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Meta de Poupança ({porcentagem_guardar}%)</div><div class="metric-value" style="color: #2e7d32;">R$ {valor_guardar:,.2f}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Contas Fixas Média</div><div class="metric-value" style="color: #c62828;">R$ {contas_fixas:,.2f}</div></div>', unsafe_allow_html=True)

st.markdown("")

# Cartão de Destaque para o Saldo Livre (Apenas exibe se houver renda digitada)
if renda_total > 0:
    if saldo_livre >= 0:
        st.success(f"### 🎉 Saldo Livre para o Mês: **R$ {saldo_livre:,.2f}**")
        st.caption("Este é o valor disponível para mercado, lazer, gasolina, manutenção (carro, moto, ap), etc.")
    else:
        st.error(f"### ⚠️ Atenção! Orçamento estourado em: **R$ {abs(saldo_livre):,.2f}**")
        st.caption("A soma das contas fixas e da meta de poupança superou a sua renda este mês. Ajuste a porcentagem ou reduza custos.")

    # --- TABELA DE DISTRIBUIÇÃO ---
    st.markdown("#### 📋 Divisão Percentual do Orçamento")
    
    # Criando um DataFrame limpo usando o Pandas do seu requirements
    p_poupança = (valor_guardar / renda_total) * 100
    p_fixas = (contas_fixas / renda_total) * 100
    p_livre = (max(0.0, saldo_livre) / renda_total) * 100

    df_distribuicao = pd.DataFrame({
        "Destino do Dinheiro": ["Poupança (Meta)", "Contas Fixas Proporcionais", "Saldo Livre (Variáveis)"],
        "Valor (R$)": [f"R$ {valor_guardar:,.2f}", f"R$ {contas_fixas:,.2f}", f"R$ {max(0.0, saldo_livre):,.2f}"],
        "Porcentagem do Salário": [f"{p_poupança:.1f}%", f"{p_fixas:.1f}%", f"{p_livre:.1f}%"]
    })
    
    # Exibe uma tabela nativa e elegante do Streamlit
    st.dataframe(df_distribuicao, hide_index=True, use_container_width=True)

else:
    st.info("💡 Insira os valores de Adiantamento e Pagamento acima para gerar o seu diagnóstico financeiro.")

st.divider()

# --- DETALHAMENTO DE CONTAS FIXAS ---
with st.expander("📌 Ver lista de contas fixas inclusas no cálculo (R$ 2.200,00)"):
    st.write("Abaixo estão as contas cobertas pelo seu teto fixo mensal:")
    st.markdown("""
    * 🏠 **Financiamento do Apartamento**
    * 🏙️ **Condomínio**
    * 📄 **IPTU**
    * 🌐 **Claro (Internet e TV)**
    * ⚡ **Conta de Luz**
    * 📱 **Conta de Celular**
    * 🛡️ **Seguro Residencial**
    """)
    st.info("Nota: Gastos como mercado, lazer, gasolina e manutenção devem ser custeados pelo **Saldo Livre**.")

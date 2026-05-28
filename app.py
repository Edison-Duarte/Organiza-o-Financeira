import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Gestão Financeira + Extrato", page_icon="💰", layout="centered")

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

st.title("💰 Gestão Financeira com Histórico Real")

# --- CONEXÃO COM O BANCO DE DADOS (GOOGLE SHEETS) ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Lê os dados existentes na planilha (aba Gastos)
    df_gastos_reais = conn.read(worksheet="Gastos", ttl="0m")
except Exception as e:
    st.error("Erro ao conectar com o Google Sheets. Verifique as Secrets no Streamlit Cloud.")
    df_gastos_reais = pd.DataFrame(columns=["Data", "Descricao", "Categoria", "Valor"])

# --- SEÇÃO 1: ENTRADAS DE RENDA FIXA (Mantida na memória da sessão) ---
# Para simplificar o fluxo inicial, mantemos a renda base estática em tela
st.subheader("📥 Recebimentos Base")
col1, col2 = st.columns(2)
with col1:
    adiantamento = st.number_input("Adiantamento (Dia 20) - R$", min_value=0.0, value=2082.22, format="%.2f")
with col2:
    salario_oficial = st.number_input("Pagamento Oficial (Dia 05) - R$", min_value=0.0, value=3152.25, format="%.2f")

renda_total = adiantamento + salario_oficial
porcentagem_guardar = st.slider("Porcentagem para guardar (Meta):", min_value=0, max_value=100, value=10, step=5)
valor_guardar = renda_total * (porcentagem_guardar / 100)

st.divider()

# --- SEÇÃO 2: NOVO LANÇAMENTO DE GASTO REAL ---
st.subheader("💸 Lançar Novo Gasto")
st.write("Registrou uma despesa? Coloque aqui para computar no gráfico:")

with st.form(key="novo_gasto_form", clear_on_submit=True):
    col_data, col_desc = st.columns([1, 2])
    with col_data:
        data_gasto = st.date_input("Data", datetime.now())
    with col_desc:
        descricao_gasto = st.text_input("Descrição (Ex: Bar do Fulano, Mercado X)")
        
    col_cat, col_val = st.columns(2)
    with col_cat:
        categoria_gasto = st.selectbox("Categoria", ["Mercado", "Saídas/Lazer", "Passeios/Viagens", "Combustível Carro", "Combustível Moto", "Contas Fixas", "Outros"])
    with col_val:
        valor_lancado = st.number_input("Valor Pago - R$", min_value=0.01, step=5.0, format="%.2f")
        
    botao_salvar = st.form_submit_button("Gravar Gasto na Planilha", type="primary", use_container_width=True)

    if botao_salvar:
        if descricao_gasto == "":
            st.warning("Por favor, digite uma descrição para o gasto.")
        else:
            # Preparar nova linha para a planilha
            novo_dado = pd.DataFrame([{
                "Data": data_gasto.strftime("%Y-%m-%d"),
                "Descricao": descricao_gasto,
                "Categoria": categoria_gasto,
                "Valor": float(valor_lancado)
            }])
            
            # Combinar dado antigo com o novo e salvar
            df_atualizado = pd.concat([df_gastos_reais, novo_dado], ignore_index=True)
            conn.update(worksheet="Gastos", data=df_atualizado)
            st.success(f"🎉 '{descricao_gasto}' gravado com sucesso! Atualizando painel...")
            # Força o recarregamento dos dados reais
            st.rerun()

st.divider()

# --- SEÇÃO 3: ANÁLISE REAL DOS GASTOS ---
st.subheader("📊 Gráficos e Distribuição dos Gastos Reais")

if not df_gastos_reais.empty and len(df_gastos_reais) > 0:
    # Garante que a coluna de Valor está em formato numérico
    df_gastos_reais["Valor"] = pd.to_numeric(df_gastos_reais["Valor"])
    
    # Agrupa gastos por Categoria
    df_agrupado = df_gastos_reais.groupby("Categoria")["Valor"].sum().reset_index()
    total_gasto_real = df_agrupado["Valor"].sum()
    
    # Calcula as porcentagens em relação ao gasto total acumulado
    df_agrupado["Porcentagem do Total Gasto"] = (df_agrupado["Valor"] / total_gasto_real) * 100
    df_agrupado["Porcentagem do Salário"] = (df_agrupado["Valor"] / renda_total) * 100 if renda_total > 0 else 0
    
    # Exibe Gráfico de Barras nativo do Streamlit
    st.bar_chart(data=df_agrupado, x="Categoria", y="Valor", color="#1e3d59")
    
    # Tabela formatada para visualização rápida
    st.markdown("#### 📋 Resumo por Categoria")
    df_exibicao = df_agrupado.copy()
    df_exibicao["Valor"] = df_exibicao["Valor"].map("R$ {:,.2f}".format)
    df_exibicao["Porcentagem do Total Gasto"] = df_exibicao["Porcentagem do Total Gasto"].map("{:.1f}%".format)
    df_exibicao["Porcentagem do Salário"] = df_exibicao["Porcentagem do Salário"].map("{:.1f}%".format)
    
    st.dataframe(df_exibicao, hide_index=True, use_container_width=True)
    
    # --- CALCULO DO SALDO LIVRE DINÂMICO ---
    saldo_livre_real = renda_total - valor_guardar - total_gasto_real
else:
    total_gasto_real = 0.0
    saldo_livre_real = renda_total - valor_guardar
    st.info("💡 Nenhuma despesa real foi lançada ainda. Use o formulário acima para começar.")

st.divider()

# --- SEÇÃO 4: PAINEL DE FECHAMENTO ---
st.subheader("🏁 Balanço de Sobra Atual")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Renda Total</div><div class="metric-value">R$ {renda_total:,.2f}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Guardado (Meta)</div><div class="metric-value" style="color: #2e7d32;">R$ {valor_guardar:,.2f}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Total Gasto Real</div><div class="metric-value" style="color: #c62828;">R$ {total_gasto_real:,.2f}</div></div>', unsafe_allow_html=True)

st.markdown("")

if renda_total > 0:
    if saldo_livre_real >= 0:
        st.success(f"### 🎉 Saldo Disponível na Conta: **R$ {saldo_livre_real:,.2f}**")
        st.caption("Este é o valor que teoricamente ainda sobrou na sua conta corrente após os gastos reais computados e a meta de poupança separada.")
    else:
        st.error(f"### ⚠️ Atenção! Você gastou mais do que devia em: **R$ {abs(saldo_livre_real):,.2f}**")

    # --- LISTA COMPLETA DE EXTRATO ---
    if not df_gastos_reais.empty:
        st.markdown("#### 📜 Extrato Detalhado do Mês")
        df_extrato = df_gastos_reais.sort_values(by="Data", ascending=False).copy()
        df_extrato["Valor"] = df_extrato["Valor"].map("R$ {:,.2f}".format)
        st.dataframe(df_extrato, hide_index=True, use_container_width=True)

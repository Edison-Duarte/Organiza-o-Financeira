import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página (Deve ser a primeira linha)
st.set_page_config(page_title="Gestão Financeira + Extrato", page_icon="💰", layout="centered")

# Estilização de cartões e blocos visuais
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
    .metric-value { font-size: 21px; color: #1e3d59; font-weight: bold; }
    
    .card-dia {
        background-color: #f8f9fa;
        padding: 18px;
        border-radius: 8px;
        border-left: 5px solid #1e3d59;
        margin-bottom: 15px;
    }
    .card-title { font-size: 16px; font-weight: bold; color: #1e3d59; margin-bottom: 10px; }
    .proj-item { font-size: 14px; margin-bottom: 4px; color: #333; }
    </style>
""", unsafe_allow_html=True)

st.title("💰 Gestão Financeira Pessoal")

# --- CONEXÃO DIRETA E SEGURA VIA PANDAS (LEITURA) ---
SHEET_ID = "1X74m1kSZIx_eLdGTb8ZOf4RNK-PrFWFlmdx4gtgig9Q"
URL_PANDAS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Gastos"

try:
    df_gastos_reais = pd.read_csv(URL_PANDAS)
    df_gastos_reais = df_gastos_reais.dropna(how="all", axis=1)
    for col in ["Data", "Descricao", "Categoria", "Valor"]:
        if col not in df_gastos_reais.columns:
            df_gastos_reais[col] = None
except Exception as e:
    df_gastos_reais = pd.DataFrame(columns=["Data", "Descricao", "Categoria", "Valor"])

# --- SEÇÃO 1: ENTRADAS DE RENDA ---
st.subheader("📥 Recebimentos Base")
col1, col2 = st.columns(2)
with col1:
    adiantamento = st.number_input("Adiantamento (Dia 20) - R$", min_value=0.0, value=2082.22, format="%.2f")
with col2:
    salario_oficial = st.number_input("Pagamento Oficial (Dia 05) - R$", min_value=0.0, value=3152.25, format="%.2f")

renda_total = adiantamento + salario_oficial
porcentagem_guardar = st.slider("Porcentagem para guardar (% Meta de Poupança):", min_value=0, max_value=100, value=10, step=5)
valor_guardar = renda_total * (porcentagem_guardar / 100)

st.divider()

# --- SEÇÃO 2: QUADROS DE PROJEÇÃO ESTÁTICA (DIA 20 E DIA 05) ---
st.subheader("📋 Planejamento Estratégico (Projeções)")
st.caption("Suas metas ideais de divisão baseadas no dia do pagamento:")

col_card1, col_card2 = st.columns(2)

with col_card1:
    st.markdown(f"""
    <div class="card-dia">
        <div class="card-title">🎯 Bloco Dia 20 (Adiantamento)</div>
        <div class="proj-item"><b>Mercado (30%):</b> R$ {adiantamento * 0.30:,.2f}</div>
        <div class="proj-item"><b>Lazer / Saídas (25%):</b> R$ {adiantamento * 0.25:,.2f}</div>
        <div class="proj-item"><b>Combustível Moto (15%):</b> R$ {adiantamento * 0.15:,.2f}</div>
        <div class="proj-item"><b>Combustível Carro (20%):</b> R$ {adiantamento * 0.20:,.2f}</div>
        <div class="proj-item"><b>Outros / Reserva (10%):</b> R$ {adiantamento * 0.10:,.2f}</div>
        <hr style="margin: 8px 0; border: 0; border-top: 1px solid #ddd;">
        <div style="font-size: 13px; color: #666;"><b>Total Alocado:</b> R$ {adiantamento:,.2f} (100%)</div>
    </div>
    """, unsafe_allow_html=True)

with col_card2:
    st.markdown(f"""
    <div class="card-dia">
        <div class="card-title">🎯 Bloco Dia 05 (Salário Oficial)</div>
        <div class="proj-item"><b>Contas Fixas (45%):</b> R$ {salario_oficial * 0.45:,.2f}</div>
        <div class="proj-item"><b>Passeios / Viagens (20%):</b> R$ {salario_oficial * 0.20:,.2f}</div>
        <div class="proj-item"><b>Mercado - Extra (15%):</b> R$ {salario_oficial * 0.15:,.2f}</div>
        <div class="proj-item"><b>Lazer / Saídas (10%):</b> R$ {salario_oficial * 0.10:,.2f}</div>
        <div class="proj-item"><b>Outros / Extras (10%):</b> R$ {salario_oficial * 0.10:,.2f}</div>
        <hr style="margin: 8px 0; border: 0; border-top: 1px solid #ddd;">
        <div style="font-size: 13px; color: #666;"><b>Total Alocado:</b> R$ {salario_oficial:,.2f} (100%)</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# --- SEÇÃO 3: LANÇAMENTO DE GASTO REAL ---
st.subheader("💸 Lançar Novo Gasto Efetuado")

with st.form(key="novo_gasto_form", clear_on_submit=True):
    col_data, col_desc = st.columns([1, 2])
    with col_data:
        data_gasto = st.date_input("Data", datetime.now())
    with col_desc:
        descricao_gasto = st.text_input("Descrição do gasto (Ex: Bar do fulano, Supermercado Extra)")
        
    col_cat, col_val = st.columns(2)
    with col_cat:
        categoria_gasto = st.selectbox("Categoria do Gasto", ["Mercado", "Saídas/Lazer", "Passeios/Viagens", "Combustível Carro", "Combustível Moto", "Contas Fixas", "Outros"])
    with col_val:
        valor_lancado = st.number_input("Valor total pago - R$", min_value=0.01, step=5.0, format="%.2f")
        
    botao_salvar = st.form_submit_button("Gravar Gasto na Planilha", type="primary", use_container_width=True)

    if botao_salvar:
        if descricao_gasto == "":
            st.warning("Por favor, preencha a descrição antes de salvar.")
        else:
            try:
                from streamlit_gsheets import GSheetsConnection
                conn = st.connection("gsheets", type=GSheetsConnection)
                df_existente = conn.read(worksheet="Gastos", ttl="0m")
                
                novo_dado = pd.DataFrame([{
                    "Data": data_gasto.strftime("%Y-%m-%d"),
                    "Descricao": descricao_gasto,
                    "Categoria": categoria_gasto,
                    "Valor": float(valor_lancado)
                }])
                
                df_atualizado = pd.concat([df_existente, novo_dado], ignore_index=True)
                conn.update(worksheet="Gastos", data=df_atualizado)
                st.success(f"🎉 '{descricao_gasto}' gravado com sucesso no Google Sheets!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro técnico ao salvar na planilha: {e}")

st.divider()

# --- SEÇÃO 4: GRÁFICOS E ANÁLISE REAL ---
st.subheader("📊 Gráficos e Distribuição dos Gastos Reais")

df_gastos_reais = df_gastos_reais.dropna(subset=["Valor"])

if not df_gastos_reais.empty and len(df_gastos_reais) > 0:
    df_gastos_reais["Valor"] = pd.to_numeric(df_gastos_reais["Valor"])
    df_agrupado = df_gastos_reais.groupby("Categoria")["Valor"].sum().reset_index()
    total_gasto_real = df_agrupado["Valor"].sum()
    
    df_agrupado["% do Total Gasto Real"] = (df_agrupado["Valor"] / total_gasto_real) * 100
    df_agrupado["% do Seu Salário Total"] = (df_agrupado["Valor"] / renda_total) * 100 if renda_total > 0 else 0
    
    # Exibe Gráfico de Barras nativo
    st.bar_chart(data=df_agrupado, x="Categoria", y="Valor", color="#1e3d59")
    
    # Exibe Tabela de Resumo Dinâmico
    st.markdown("#### 📋 Consolidado Atual por Categoria")
    df_exibicao = df_agrupado.copy()
    df_exibicao["Valor"] = df_exibicao["Valor"].map("R$ {:,.2f}".format)
    df_exibicao["% do Total Gasto Real"] = df_exibicao["% do Total Gasto Real"].map("{:.1f}%".format)
    df_exibicao["% do Seu Salário Total"] = df_exibicao["% do Seu Salário Total"].map("{:.1f}%".format)
    
    st.dataframe(df_exibicao, hide_index=True, use_container_width=True)
    saldo_livre_real = renda_total - valor_guardar - total_gasto_real
else:
    total_gasto_real = 0.0
    saldo_livre_real = renda_total - valor_guardar
    st.info("💡 Nenhum gasto real computado para este mês ainda. Use o formulário acima.")

st.divider()

# --- SEÇÃO 5: BALANÇO DE SOBRA REAL DE CAIXA ---
st.subheader("🏁 Balanço de Sobra Atual")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Renda Total</div><div class="metric-value">R$ {renda_total:,.2f}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Guardado (Meta)</div><div class="metric-value" style="color: #2e7d32;">R$ {valor_guardar:,.2f}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Total Gasto Real</div><div class="metric-value" style="color: #c62828;">R$ {total_gasto_real:,.2f}</div></div>', unsafe_allow_html=True)

if renda_total > 0:
    st.markdown("")
    if saldo_livre_real >= 0:
        st.success(f"### 🎉 Saldo Disponível em Conta: **R$ {saldo_livre_real:,.2f}**")
    else:
        st.error(f"### ⚠️ Atenção! Orçamento estourado em: **R$ {abs(saldo_livre_real):,.2f}**")

    if not df_gastos_reais.empty and len(df_gastos_reais) > 0:
        st.markdown("#### 📜 Extrato Detalhado de Lançamentos")
        df_extrato = df_gastos_reais.sort_values(by="Data", ascending=False).copy()
        df_extrato["Valor"] = df_extrato["Valor"].map("R$ {:,.2f}".format)
        st.dataframe(df_extrato, hide_index=True, use_container_width=True)

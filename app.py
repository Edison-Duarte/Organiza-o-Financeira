import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# Configuração da página (Deve ser a primeira linha)
st.set_page_config(page_title="Gestão Financeira + Extrato", page_icon="💰", layout="centered")

# Estilização para recriar os quadros informativos azuis do projeto financeiro
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
    
    .card-info-azul {
        background-color: #e8f0fe;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #c2dbff;
        margin-bottom: 15px;
        min-height: 280px;
    }
    .card-info-titulo { font-size: 20px; font-weight: bold; color: #1967d2; margin-bottom: 12px; }
    .card-info-sub { font-size: 14px; color: #1e3d59; font-weight: bold; margin-bottom: 8px; }
    .card-info-insight { font-size: 13px; color: #5f6368; font-style: italic; margin-bottom: 15px; }
    .card-info-lista { font-size: 14px; color: #3c4043; margin-left: 5px; margin-bottom: 6px; }
    .card-info-total { font-size: 13px; color: #1967d2; font-weight: bold; margin-top: 12px; border-top: 1px dashed #c2dbff; padding-top: 8px; }
    </style>
""", unsafe_allow_html=True)

fuso_br = pytz.timezone('America/Sao_Paulo')
def obter_agora_br():
    return datetime.now(fuso_br)

st.title("💰 Gestão Financeira com Histórico Real")

# --- CONEXÃO DIRETA E SEGURA VIA PANDAS (LEITURA) ---
SHEET_ID = "1X74m1kSZIx_eLdGTb8ZOf4RNK-PrFWFlmdx4gtgig9Q"
URL_PANDAS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Gastos"

try:
    df_gastos_reais = pd.read_csv(URL_PANDAS)
    df_gastos_reais = df_gastos_reais.dropna(how="all", axis=1)
    # Garante cabeçalhos corretos do financeiro
    for col in ["Data", "Descricao", "Categoria", "Valor"]:
        if col not in df_gastos_reais.columns:
            df_gastos_reais[col] = None
except Exception:
    df_gastos_reais = pd.DataFrame(columns=["Data", "Descricao", "Categoria", "Valor"])

# --- SEÇÃO 1: RECEBIMENTOS DO MÊS ---
st.subheader("📥 Recebimentos do Mês")
col1, col2 = st.columns(2)
with col1:
    adiantamento = st.number_input("Adiantamento (Dia 20) - R$", min_value=0.0, value=2082.22, format="%.2f")
with col2:
    salario_oficial = st.number_input("Pagamento Oficial (Dia 05) - R$", min_value=0.0, value=3152.25, format="%.2f")

renda_total = adiantamento + salario_oficial
porcentagem_guardar = st.slider("Porcentagem que deseja guardar este mês:", min_value=0, max_value=100, value=10, step=5)
poupança_total = renda_total * (porcentagem_guardar / 100)

st.divider()

# --- SEÇÃO 2: PROJEÇÕES DE GASTOS VARIÁVEIS E FIXOS ---
st.subheader("🚗 Gastos Variáveis do Mês (Previsão)")
col_v1, col_v2, col_v3 = st.columns(3)
with col_v1:
    proj_mercado = st.number_input("Supermercado / Alimentação - R$", min_value=0.0, value=750.00, format="%.2f")
with col_v2:
    proj_moto = st.number_input("Combustível: Moto - R$", min_value=0.0, value=120.00, format="%.2f")
with col_v3:
    proj_carro = st.number_input("Combustível: Carro - R$", min_value=0.0, value=250.00, format="%.2f")

variaveis_previstas = proj_mercado + proj_moto + proj_carro

st.subheader("📌 Detalhamento das Contas Fixas (Previsão)")
col_f1, col_f2 = st.columns(2)
with col_f1:
    f_financiamento = st.number_input("Financiamento do Ap - R$", min_value=0.0, value=1400.00, format="%.2f")
    f_condominio = st.number_input("Condomínio - R$", min_value=0.0, value=400.00, format="%.2f")
    f_iptu = st.number_input("IPTU - R$", min_value=0.0, value=100.00, format="%.2f")
    f_seguro = st.number_input("Seguro Residencial - R$", min_value=0.0, value=30.00, format="%.2f")
with col_f2:
    f_claro = st.number_input("Claro (Internet/TV) - R$", min_value=0.0, value=150.00, format="%.2f")
    f_luz = st.number_input("Conta de Luz - R$", min_value=0.0, value=80.00, format="%.2f")
    f_celular = st.number_input("Conta de Celular - R$", min_value=0.0, value=40.00, format="%.2f")

contas_fixas_total = f_financiamento + f_condominio + f_iptu + f_seguro + f_claro + f_luz + f_celular
comprometido_total = contas_fixas_total + variaveis_previstas
saldo_livre_lazer = renda_total - poupança_total - comprometido_total

st.divider()

# --- SEÇÃO 3: RESUMO FINANCEIRO E PAINEL METODOLÓGICO DOS DIAS ---
st.subheader("📊 Resumo Financeiro Projetado")
cq1, cq2, cq3, cq4 = st.columns(4)
cq1.markdown(f'<div class="metric-box"><div class="metric-title">Renda Total</div><div class="metric-value">R$ {renda_total:,.2f}</div></div>', unsafe_allow_html=True)
cq2.markdown(f'<div class="metric-box"><div class="metric-title">Poupança Total</div><div class="metric-value" style="color: #2e7d32;">R$ {poupança_total:,.2f}</div></div>', unsafe_allow_html=True)
cq3.markdown(f'<div class="metric-box"><div class="metric-title">Contas Fixas</div><div class="metric-value" style="color: #c62828;">R$ {contas_fixas_total:,.2f}</div></div>', unsafe_allow_html=True)
cq4.markdown(f'<div class="metric-box"><div class="metric-title">Variáveis Previstas</div><div class="metric-value" style="color: #ef6c00;">R$ {variaveis_previstas:,.2f}</div></div>', unsafe_allow_html=True)

st.info(f"🎉 **Saldo Livre Estimado para Lazer/Hobbies:** R$ {saldo_livre_lazer:,.2f}")

st.subheader("📅 O que fazer quando o dinheiro cair?")

proporcao_adiantamento = adiantamento / renda_total if renda_total > 0 else 0
proporcao_salario = salario_oficial / renda_total if renda_total > 0 else 0

poup_dia20 = adiantamento * (porcentagem_guardar / 100)
contas_dia20 = comprometido_total * proporcao_adiantamento
retencao_dia20_total = poup_dia20 + contas_dia20
pct_reter_dia20 = (retencao_dia20_total / adiantamento) * 100 if adiantamento > 0 else 0
pct_do_salario_total_dia20 = (retencao_dia20_total / renda_total) * 100 if renda_total > 0 else 0

poup_dia05 = salario_oficial * (porcentagem_guardar / 100)
contas_dia05 = comprometido_total * proporcao_salario
retencao_dia05_total = poup_dia05 + contas_dia05
pct_reter_dia05 = (retencao_dia05_total / salario_oficial) * 100 if salario_oficial > 0 else 0
pct_do_salario_total_dia05 = (retencao_dia05_total / renda_total) * 100 if renda_total > 0 else 0

col_card1, col_card2 = st.columns(2)

with col_card1:
    st.markdown(f"""
    <div class="card-info-azul">
        <div class="card-info-titulo">🏙️ Dia 20 (Adiantamento)</div>
        <div class="card-info-sub">Você deve reter {pct_reter_dia20:.1f}% deste adiantamento.</div>
        <div class="card-info-insight">💡 Isso equivale a {pct_do_salario_total_dia20:.1f}% do seu salário total.</div>
        <div class="card-info-lista">🔹 <b>Poupar (Meta):</b> R$ {poup_dia20:,.2f}</div>
        <div class="card-info-lista">🔹 <b>Reservar para Contas:</b> R$ {contas_dia20:,.2f}</div>
        <div class="card-info-total">**Total a reter/guardar:** R$ {retencao_dia20_total:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with col_card2:
    st.markdown(f"""
    <div class="card-info-azul">
        <div class="card-info-titulo">🩻 Dia 05 (Pagamento Oficial)</div>
        <div class="card-info-sub">Você deve reter {pct_reter_dia05:.1f}% deste pagamento.</div>
        <div class="card-info-insight">💡 Isso equivale a {pct_do_salario_total_dia05:.1f}% do seu salário total.</div>
        <div class="card-info-lista">🔹 <b>Poupar (Meta):</b> R$ {poup_dia05:,.2f}</div>
        <div class="card-info-lista">🔹 <b>Separar para Contas:</b> R$ {contas_dia05:,.2f}</div>
        <div class="card-info-total">**Total a reter/guardar:** R$ {retencao_dia05_total:,.2f}</div>
        <div style="font-size: 11px; color: #c62828; margin-top: 4px; font-weight: bold;">📌 Junte com a reserva do dia 20 para pagar os boletos.</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# --- SEÇÃO 4: LANÇAMENTO DE GASTO REAL NO GOOGLE SHEETS ---
st.subheader("💸 Lançar Novo Gasto Efetuado (Real)")

with st.form(key="novo_gasto_form", clear_on_submit=True):
    col_data, col_desc = st.columns([1, 2])
    with col_data:
        data_gasto = st.date_input("Data do Pagamento", obter_agora_br())
    with col_desc:
        descricao_gasto = st.text_input("Descrição (Ex: Compras Mensais, Posto Shell)")
        
    col_cat, col_val = st.columns(2)
    with col_cat:
        categoria_gasto = st.selectbox("Categoria", ["Mercado", "Saídas/Lazer", "Passeios/Viagens", "Combustível Carro", "Combustível Moto", "Contas Fixas", "Outros"])
    with col_val:
        valor_lancado = st.number_input("Valor Pago - R$", min_value=0.01, step=5.0, format="%.2f")
        
    botao_salvar = st.form_submit_button("Gravar Gasto na Planilha", type="primary", use_container_width=True)

    if botao_salvar:
        if descricao_gasto == "":
            st.warning("Insira uma descrição para salvar.")
        else:
            with st.spinner("Gravando dados na planilha..."):
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
                    
                    st.success(f"🎉 '{descricao_gasto}' guardado com sucesso!")
                    st.rerun()
                    
                except Exception as e:
                    if "200" in str(e):
                        st.success(f"🎉 '{descricao_gasto}' guardado com sucesso!")
                        st.rerun()
                    else:
                        st.error(f"Erro ao salvar: {e}")

st.divider()

# --- SEÇÃO 5: EXTRAÇÃO E COMPARATIVO DO REAL ---
st.subheader("📉 Extrato Histórico e Lançamentos do Mês")

df_gastos_reais = df_gastos_reais.dropna(subset=["Valor"])

if not df_gastos_reais.empty and len(df_gastos_reais) > 0:
    df_gastos_reais["Valor"] = pd.to_numeric(df_gastos_reais["Valor"])
    df_agrupado = df_gastos_reais.groupby("Categoria")["Valor"].sum().reset_index()
    total_gasto_real = df_agrupado["Valor"].sum()
    
    st.bar_chart(data=df_agrupado, x="Categoria", y="Valor", color="#1e3d59")
    
    df_exibicao = df_agrupado.copy()
    df_exibicao["Valor"] = df_exibicao["Valor"].map("R$ {:,.2f}".format)
    st.dataframe(df_exibicao, hide_index=True, use_container_width=True)
    
    saldo_real_caixa = renda_total - poupança_total - total_gasto_real
    if saldo_real_caixa >= 0:
        st.success(f"### 💳 Saldo Atual em Conta (Real): **R$ {saldo_real_caixa:,.2f}**")
    else:
        st.error(f"### ⚠️ Caixa estourado em: **R$ {abs(saldo_real_caixa):,.2f}**")
        
    df_extrato = df_gastos_reais.sort_values(by="Data", ascending=False).copy()
    df_extrato["Valor"] = df_extrato["Valor"].map("R$ {:,.2f}".format)
    st.dataframe(df_extrato, hide_index=True, use_container_width=True)
else:
    st.info("💡 Nenhum gasto real computado ainda na planilha.")

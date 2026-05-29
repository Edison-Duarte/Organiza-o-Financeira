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

# --- MAPEAMENTO E SOMA DE GASTOS REAIS DA PLANILHA ---
df_planilha = carregar_gastos_reais()

soma_mercado = 0.0
soma_carro = 0.0
soma_moto = 0.0
soma_fixas = 0.0
soma_lazer = 0.0

if not df_planilha.empty and "Categoria" in df_planilha.columns and "Valor" in df_planilha.columns:
    # Garante que os valores estão lidos como números
    df_planilha["Valor"] = pd.to_numeric(df_planilha["Valor"], errors='coerce').fillna(0.0)
    
    # Agrupa e soma por categoria
    somas_por_cat = df_planilha.groupby("Categoria")["Valor"].sum()
    
    soma_mercado = float(somas_por_cat.get("Supermercado / Alimentação", 0.0))
    soma_moto = float(somas_por_cat.get("Combustível: Moto", 0.0))
    soma_carro = float(somas_por_cat.get("Combustível: Carro", 0.0))
    soma_fixas = float(somas_por_cat.get("Contas Fixas", 0.0))
    soma_lazer = float(somas_por_cat.get("Outros / Lazer", 0.0))

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

# O total de previstos permanece baseado nas suas estimativas do topo
gastos_variaveis_total = compras_mes + combustivel_carro + combustivel_moto
# Soma do que de fato já foi consumido de variáveis na planilha
total_gastos_variaveis_realizados = soma_mercado + soma_carro + soma_moto

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

st.divider()

# --- CÁLCULOS FINANCEIROS ATUALIZADOS COM ABATIMENTO REAL ---
valor_guardar = renda_total * (porcentagem_guardar / 100)

if renda_total > 0:
    # MATEMÁTICA REAL: Saldo livre inicial planejado MENOS o que você já gastou efetivamente em Lazer/Outros
    saldo_inicial_lazer = renda_total - valor_guardar - contas_fixas_total - gastos_variaveis_total
    saldo_livre_atualizado = saldo_inicial_lazer - soma_lazer
    
    p_adiantamento = adiantamento / renda_total
    p_oficial = salario_oficial / renda_total
    
    # Proporções e Totais do Adiantamento (Dia 20)
    poupança_dia20 = adiantamento * (porcentagem_guardar / 100)
    fixas_dia20 = contas_fixas_total * p_adiantamento
    total_reter_dia20 = poupança_dia20 + fixas_dia20
    porcentagem_reter_dia20 = (total_reter_dia20 / adiantamento) * 100 if adiantamento > 0 else 0
    p_reter_d20_do_total = (total_reter_dia20 / renda_total) * 100
    
    # Proporções e Totais do Pagamento Oficial (Dia 05)
    poupança_dia05 = salario_oficial * (porcentagem_guardar / 100)
    fixas_dia05 = contas_fixas_total * p_oficial
    total_reter_dia05 = poupança_dia05 + fixas_dia05
    porcentagem_reter_dia05 = (total_reter_dia05 / salario_oficial) * 100 if salario_oficial > 0 else 0
    p_reter_d05_do_total = (total_reter_dia05 / renda_total) * 100
else:
    saldo_livre_atualizado = 0.0
    porcentagem_reter_dia20 = 0.0
    total_reter_dia20 = 0.0
    p_reter_d20_do_total = 0.0
    poupança_dia20 = 0.0
    fixas_dia20 = 0.0
    
    porcentagem_reter_dia05 = 0.0
    total_reter_dia05 = 0.0
    p_reter_d05_do_total = 0.0
    poupança_dia05 = 0.0
    fixas_dia05 = 0.0

# --- SEÇÃO 4: PAINEL DE RESULTADOS DINÂMICO ---
st.subheader("📊 Resumo Financeiro Real")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Renda Total</div><div class="metric-value">R$ {renda_total:,.2f}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-box"><div class="metric-title">Poupança Total</div><div class="metric-value" style="color: #2e7d32;">R$ {valor_guardar:,.2f}</div></div>', unsafe_allow_html=True)
with c3:
    # Exibe o planejado vs quanto já foi pago de contas fixas
    st.markdown(f'<div class="metric-box"><div class="metric-title">Contas Fixas (Pagas)</div><div class="metric-value" style="color: #c62828;">R$ {soma_fixas:,.2f} <span style="font-size:12px; color:#777;">/ {contas_fixas_total:,.2f}</span></div></div>', unsafe_allow_html=True)
with c4:
    # Exibe o previsto vs quanto já consumiu do teto de variáveis
    st.markdown(f'<div class="metric-box"><div class="metric-title">Variáveis (Gastos)</div><div class="metric-value" style="color: #f57c00;">R$ {total_gastos_variaveis_realizados:,.2f} <span style="font-size:12px; color:#777;">/ {gastos_variaveis_total:,.2f}</span></div></div>', unsafe_allow_html=True)

st.markdown("")

if renda_total > 0:
    if saldo_livre_atualizado >= 0:
        st.success(f"### 🎉 Saldo Livre Atual para Lazer: **R$ {saldo_livre_atualizado:,.2f}**")
    else:
        st.error(f"### ⚠️ Atenção! Orçamento de Lazer estourado em: **R$ {abs(saldo_livre_atualizado):,.2f}**")

    st.divider()
    st.subheader("📅 O que fazer quando o dinheiro cair?")
    
    col_d20, col_d05 = st.columns(2)
    with col_d20:
        st.info(f"### 🏦 Dia 20 (Adiantamento)\n"
                f"Você deve reter **{porcentagem_reter_dia20:.1f}%** deste adiantamento.\n\n"
                f"💡 *Isso equivale a **{p_reter_d20_do_total:.1f}%** do seu salário total.*\n\n"
                f"* **Poupar (Meta):** R$ {poupança_dia20:,.2f}\n"
                f"* **Reservar para Contas:** R$ {fixas_dia20:,.2f}\n"
                f"**Total a reter/guardar:** R$ {total_reter_dia20:,.2f}")
                
    with col_d05:
        st.info(f"### 🏢 Dia 05 (Pagamento Oficial)\n"
                f"Você deve reter **{porcentagem_reter_dia05:.1f}%** deste pagamento.\n\n"
                f"💡 *Isso equivale a **{p_reter_d05_do_total:.1f}%** do seu salário total.*\n\n"
                f"* **Poupar (Meta):** R$ {poupança_dia05:,.2f}\n"
                f"* **Separar para Contas:** R$ {fixas_dia05:,.2f}\n"
                f"**Total a reter/guardar:** R$ {total_reter_dia05:,.2f}\n\n"
                f"📌 *Junte com a reserva do dia 20 para pagar os boletos.*")

    st.markdown("#### 📋 Distribuição Geral do Orçamento Real")
    
    # Abas visuais de progresso de consumo do salário
    p_poupança = (valor_guardar / renda_total) * 100
    p_fixas = (contas_fixas_total / renda_total) * 100
    p_variaveis = (gastos_variaveis_total / renda_total) * 100
    p_livre = (max(0.0, saldo_livre_atualizado) / renda_total) * 100

    df_distribuicao = pd.DataFrame({
        "Destino do Dinheiro": ["Poupança (Investimentos)", "Contas Fixas (Moradia/Consumo)", "Gastos Variáveis (Mercado/Combustíveis)", "Saldo Livre Atual (Lazer/Hobbies)"],
        "Valor Limite/Teto (R$)": [f"R$ {valor_guardar:,.2f}", f"R$ {contas_fixas_total:,.2f}", f"R$ {gastos_variaveis_total:,.2f}", f"R$ {max(0.0, saldo_inicial_lazer):,.2f}"],
        "Consumido Real (R$)": [f"R$ {valor_guardar:,.2f}", f"R$ {soma_fixas:,.2f}", f"R$ {total_gastos_variaveis_realizados:,.2f}", f"R$ {soma_lazer:,.2f}"],
        "Saldo Restante (R$)": [f"R$ 0.00", f"R$ {contas_fixas_total - soma_fixas:,.2f}", f"R$ {gastos_variaveis_total - total_gastos_variaveis_realizados:,.2f}", f"R$ {max(0.0, saldo_livre_atualizado):,.2f}"]
    })
    
    st.dataframe(df_distribuicao, hide_index=True, use_container_width=True)
else:
    st.info("💡 Insira os valores de Adiantamento e Pagamento no topo para recalcular todo o ecossistema financeiro.")

# --- SEÇÃO DE PERSISTÊNCIA (SALVAR DADOS PADRÃO DO MÊS) ---
st.divider()
st.subheader("💾 Gerenciamento de Histórico")
st.write("Sempre que alterar os valores e quiser transformá-los no novo padrão de abertura do app, clique abaixo:")

if st.button("Salvar Valores Atuais como Padrão", type="primary", use_container_width=True):
    novos_dados = {
        "adiantamento": adiantamento,
        "salario_oficial": salario_oficial,
        "porcentagem_guardar": porcentagem_guardar,
        "compras_mes": compras_mes,
        "combustivel_carro": combustivel_carro,
        "combustivel_moto": combustivel_moto,
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
        st.success("🎉 Valores salvos com sucesso! No próximo acesso, o app abrirá exatamente assim.")
    except Exception as e:
        st.error(f"Erro ao salvar os dados localmente: {e}")

# =========================================================================
# SEÇÃO UNIFICADA: LANÇAMENTO DE GASTOS REAIS NO GOOGLE SHEETS
# =========================================================================
st.divider()
st.subheader("📝 Lançar Novo Gasto Efetuado (Real)")

with st.form("form_novo_gasto", clear_on_submit=True):
    data_pagamento = st.date_input("Data do Pagamento", value=agora_br)
    descricao_gasto = st.text_input("Descrição (Ex: Supermercado Carrefour, Posto Shell)")
    
    col_form1, col_form2 = st.columns(2)
    categoria_gasto = col_form1.selectbox("Categoria do Gasto", [
        "Supermercado / Alimentação", 
        "Combustível: Moto", 
        "Combustível: Carro", 
        "Contas Fixas", 
        "Outros / Lazer"
    ])
    valor_gasto = col_form2.number_input("Valor Pago - R$", min_value=0.01, value=0.01, step=0.01)
    
    botao_salvar = st.form_submit_button("Gravar Gasto na Planilha", type="primary")

if botao_salvar:
    if not descricao_gasto.strip():
        st.warning("⚠️ Por favor, insira uma descrição para salvar.")
    else:
        with st.spinner("Gravando dados na planilha..."):
            try:
                df_existente = carregar_gastos_reais()
                
                nova_linha = pd.DataFrame([{
                    "Data": data_pagamento.strftime("%Y-%m-%d"),
                    "Descricao": descricao_gasto,
                    "Categoria": categoria_gasto,
                    "Valor": float(valor_gasto)
                }])
                
                df_atualizado = pd.concat([df_existente, nova_linha], ignore_index=True)
                conn.update(worksheet="Gastos", data=df_atualizado)
                
                st.success(f"🎉 '{descricao_gasto}' gravado com sucesso!")
                st.rerun()
            except Exception as ex:
                if "200" in str(ex):
                    st.success(f"🎉 '{descricao_gasto}' gravado com sucesso!")
                    st.rerun()
                else:
                    st.error(f"Erro ao salvar na planilha: {ex}")

st.divider()
st.subheader("📜 Extrato de Lançamentos Realizados")

df_historico = carregar_gastos_reais()

if df_historico.empty:
    st.info("💡 Nenhum gasto real computado nesta aba da planilha ainda.")
else:
    df_exibir = df_historico.copy()
    if "Valor" in df_exibir.columns:
        df_exibir["Valor"] = pd.to_numeric(df_exibir["Valor"]).map("R$ {:,.2f}".format)
    
    st.dataframe(df_exibir.sort_index(ascending=False), hide_index=True, use_container_width=True)

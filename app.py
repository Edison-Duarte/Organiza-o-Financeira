import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import pytz

# --- CONFIGURAÇÕES DA PÁGINA ---
st.set_page_config(page_title="Gestão Financeira + Extrato", page_icon="📊", layout="wide")

fuso_br = pytz.timezone('America/Sao_Paulo')
def obter_agora_br():
    return datetime.now(fuso_br)

# --- CONEXÃO COM GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Erro na conexão com o Google Sheets: {e}")

# Função para carregar os gastos reais gravados na aba "Gastos"
def carregar_gastos():
    try:
        # Lê a aba/worksheet "Gastos"
        df = conn.read(worksheet="Gastos", ttl=0)
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        return df
    except Exception:
        return pd.DataFrame(columns=["Data", "Descricao", "Categoria", "Valor"])

# --- INTERFACE: ENTRADA DE DADOS DO ORÇAMENTO MENSAL ---
st.title("📊 Gestão Financeira Pessoal")

with st.expander("📌 Configurar Orçamento do Mês", expanded=False):
    st.subheader("💰 Recebimentos do Mês")
    col1, col2 = st.columns(2)
    adiantamento = col1.number_input("Adiantamento (Dia 20) - R$", value=2082.22, step=100.0)
    pagamento_oficial = col2.number_input("Pagamento Oficial (Dia 05) - R$", value=3152.25, step=100.0)
    
    porcentagem_poupar = st.slider("Porcentagem que deseja guardar este mês:", 0, 100, 10)
    
    st.subheader("🚗 Gastos Variáveis do Mês")
    col_v1, col_v2, col_v3 = st.columns(3)
    supermercado = col_v1.number_input("Supermercado / Alimentação - R$", value=750.00)
    moto = col_v2.number_input("Combustível: Moto - R$", value=120.00)
    carro = col_v3.number_input("Combustível: Carro - R$", value=250.00)
    
    st.subheader("📌 Detalhamento das Contas Fixas")
    col_f1, col_f2 = st.columns(2)
    financiamento = col_f1.number_input("Financiamento do Ap - R$", value=1400.00)
    condominio = col_f1.number_input("Condomínio - R$", value=400.00)
    iptu = col_f1.number_input("IPTU - R$", value=100.00)
    seguro = col_f1.number_input("Seguro Residencial - R$", value=30.00)
    
    claro = col_f2.number_input("Claro (Internet/TV) - R$", value=150.00)
    luz = col_f2.number_input("Conta de Luz - R$", value=80.00)
    celular = col_f2.number_input("Conta de Celular - R$", value=40.00)

# --- CÁLCULOS DO PLANEJAMENTO ---
renda_total = adiantamento + pagamento_oficial
poupanca_total = renda_total * (porcentagem_poupar / 100)
contas_fixas_total = financiamento + condominio + iptu + seguro + claro + luz + celular
variaveis_total = supermercado + moto + carro
saldo_lazer = renda_total - poupanca_total - contas_fixas_total - variaveis_total

# --- BLOCOS DE RESUMO FINANCEIRO ---
st.subheader("📊 Resumo Financeiro")
c_res1, c_res2, c_res3, c_res4 = st.columns(4)
c_res1.metric("Renda Total", f"R$ {renda_total:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."))
c_res2.metric("Poupança Total", f"R$ {poupanca_total:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."))
c_res3.metric("Contas Fixas", f"R$ {contas_fixas_total:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."))
c_res4.metric("Variáveis Previstas", f"R$ {variaveis_total:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."))

st.success(f"🎉 **Saldo Livre para Lazer: R$ {saldo_lazer:,.2f}**".replace(",", "v").replace(".", ",").replace("v", "."))

# --- FORMULÁRIO: LANÇAR NOVO GASTO REAL ---
st.divider()
st.subheader("📝 Lançar Novo Gasto Efetuado (Real)")

with st.form("form_novo_gasto", clear_on_submit=True):
    data_pagamento = st.date_input("Data do Pagamento", value=obter_agora_br().date())
    descricao_gasto = st.text_input("Descrição (Ex: Compras Mensais, Posto Shell)")
    
    col_form1, col_form2 = st.columns(2)
    categoria_gasto = col_form1.selectbox("Categoria", ["Mercado", "Combustível Moto", "Combustível Carro", "Lazer", "Contas Fixas", "Outros"])
    valor_gasto = col_form2.number_input("Valor Pago - R$", min_value=0.01, value=0.01, step=0.01)
    
    botao_salvar = st.form_submit_button("Gravar Gasto na Planilha")

if botao_salvar:
    if not descricao_gasto.strip():
        st.warning("⚠️ Insira uma descrição para salvar.")
    else:
        with st.spinner("Gravando dados..."):
            try:
                # Carrega o histórico existente para fazer o append
                df_existente = conn.read(worksheet="Gastos", ttl=0)
                df_existente = df_existente.loc[:, ~df_existente.columns.str.contains('^Unnamed')]
                
                # Prepara a nova linha
                nova_linha = pd.DataFrame([{
                    "Data": data_pagamento.strftime("%Y/%m/%d"),
                    "Descricao": descricao_gasto,
                    "Categoria": categoria_gasto,
                    "Valor": valor_gasto
                }])
                
                # Agrupa e atualiza
                df_atualizado = pd.concat([df_existente, nova_linha], ignore_index=True)
                conn.update(worksheet="Gastos", data=df_atualizado)
                st.success("✅ Gasto gravado com sucesso na planilha!")
                st.rerun()
            except Exception as ex:
                if "200" in str(ex):
                    st.success("✅ Gasto gravado com sucesso!")
                    st.rerun()
                else:
                    st.error(f"Erro ao salvar: {ex}")

# --- TABELA: EXTRATO HISTÓRICO ---
st.divider()
st.subheader("📜 Extrato Histórico e Lançamentos do Mês")

df_gastos_reais = carregar_gastos()

if df_gastos_reais.empty:
    st.info("💡 Nenhum gasto real computado ainda na planilha.")
else:
    # Formata a exibição da tabela de histórico de gastos
    df_exibicao = df_gastos_reais.copy()
    st.dataframe(df_exibicao, use_container_width=True)

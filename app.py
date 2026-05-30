import streamlit as st
import pandas as pd
import json
import os

# Configuração da página
st.set_page_config(page_title="Gestão Financeira Mensal", page_icon="💰", layout="centered")

ARQUIVO_DADOS = "dados_mes.json"

# --- FUNÇÕES DE PERSISTÊNCIA ---
def carregar_dados():
    valores_padrao = {
        "adiantamento": 2082.22, "salario_oficial": 3152.25, "porcentagem_guardar": 10,
        "compras_mes": 750.00, "combustivel_carro": 250.00, "combustivel_moto": 120.00,
        "financiamento": 1400.00, "condominio": 400.00, "iptu": 100.00,
        "seguro_residencial": 30.00, "claro_tv_internet": 150.00, "luz": 80.00, "celular": 40.00,
        "gastos_avulsos": [] # Lista para guardar gastos extras
    }
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                dados_salvos = json.load(f)
                for chave, valor in valores_padrao.items():
                    dados_salvos.setdefault(chave, valor)
                return dados_salvos
        except: return valores_padrao
    return valores_padrao

if "dados" not in st.session_state:
    st.session_state.dados = carregar_dados()

# --- INTERFACE ---
st.title("💰 Gestão de Salário & Planejamento Mensal")

# --- SEÇÕES DE ENTRADA (Abreviadas para brevidade no exemplo) ---
# [Aqui entrariam os seus inputs existentes de Renda, Variáveis e Fixas...]
# Exemplo para garantir o funcionamento:
adiantamento = st.number_input("Adiantamento", value=st.session_state.dados["adiantamento"])
salario_oficial = st.number_input("Salário Oficial", value=st.session_state.dados["salario_oficial"])
porcentagem_guardar = st.slider("Porcentagem a guardar", 0, 100, int(st.session_state.dados["porcentagem_guardar"]))
# ... (inclua os outros campos fixos aqui como você já tinha) ...

# --- NOVA SEÇÃO: GASTOS AVULSOS ---
st.subheader("📝 Adicionar Gastos Avulsos")
col_desc, col_valor, col_btn = st.columns([2, 1, 1])
with col_desc: descricao = st.text_input("Descrição (ex: Bar do Fulano)")
with col_valor: valor_extra = st.number_input("Valor (R$)", min_value=0.0, step=1.0)
with col_btn:
    st.write("###")
    if st.button("Adicionar"):
        if descricao and valor_extra > 0:
            st.session_state.dados["gastos_avulsos"].append({"desc": descricao, "valor": valor_extra})
            st.rerun()

# --- CÁLCULOS ---
renda_total = adiantamento + salario_oficial
total_extras = sum(item['valor'] for item in st.session_state.dados["gastos_avulsos"])
contas_fixas_total = 3000.00 # Exemplo: substitua pela soma real dos campos
gastos_variaveis_total = 1000.00 # Exemplo: substitua pela soma real
valor_guardar = renda_total * (porcentagem_guardar / 100)

saldo_livre = renda_total - valor_guardar - contas_fixas_total - gastos_variaveis_total - total_extras

# --- EXIBIÇÃO DE RESULTADOS ---
st.success(f"### Saldo Livre: R$ {saldo_livre:,.2f}")

if st.session_state.dados["gastos_avulsos"]:
    st.write("#### Gastos extras registrados:")
    st.table(pd.DataFrame(st.session_state.dados["gastos_avulsos"]))
    if st.button("Limpar gastos extras"):
        st.session_state.dados["gastos_avulsos"] = []
        st.rerun()

# --- BOTÃO SALVAR ---
if st.button("Salvar Tudo como Padrão", type="primary"):
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(st.session_state.dados, f, ensure_ascii=False, indent=4)
    st.success("Dados salvos!")

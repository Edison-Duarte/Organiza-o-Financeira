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
        "gastos_avulsos": [] 
    }
    
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                dados_salvos = json.load(f)
                # Proteção: Garante que a chave exista
                if "gastos_avulsos" not in dados_salvos:
                    dados_salvos["gastos_avulsos"] = []
                for chave, valor in valores_padrao.items():
                    dados_salvos.setdefault(chave, valor)
                return dados_salvos
        except: return valores_padrao
    return valores_padrao

if "dados" not in st.session_state:
    st.session_state.dados = carregar_dados()

st.title("💰 Gestão de Salário & Planejamento Mensal")

# --- SEÇÃO 1: RENDA ---
col1, col2 = st.columns(2)
with col1:
    adiantamento = st.number_input("Adiantamento (Dia 20) - R$", value=st.session_state.dados["adiantamento"], step=100.0)
with col2:
    salario_oficial = st.number_input("Pagamento Oficial (Dia 05) - R$", value=st.session_state.dados["salario_oficial"], step=100.0)

porcentagem_guardar = st.slider("Porcentagem que deseja guardar:", 0, 100, int(st.session_state.dados["porcentagem_guardar"]))

# --- SEÇÃO 2: GASTOS VARIÁVEIS E FIXOS ---
compras_mes = st.number_input("Supermercado - R$", value=st.session_state.dados["compras_mes"], step=50.0)
combustivel_carro = st.number_input("Combustível Carro - R$", value=st.session_state.dados["combustivel_carro"], step=50.0)
combustivel_moto = st.number_input("Combustível Moto - R$", value=st.session_state.dados["combustivel_moto"], step=20.0)
financiamento = st.number_input("Financiamento - R$", value=st.session_state.dados["financiamento"], step=50.0)
condominio = st.number_input("Condomínio - R$", value=st.session_state.dados["condominio"], step=20.0)
iptu = st.number_input("IPTU - R$", value=st.session_state.dados["iptu"], step=10.0)
seguro_residencial = st.number_input("Seguro Residencial - R$", value=st.session_state.dados["seguro_residencial"], step=5.0)
claro_tv_internet = st.number_input("Claro - R$", value=st.session_state.dados["claro_tv_internet"], step=10.0)
luz = st.number_input("Luz - R$", value=st.session_state.dados["luz"], step=10.0)
celular = st.number_input("Celular - R$", value=st.session_state.dados["celular"], step=5.0)

# --- NOVA SEÇÃO: GASTOS AVULSOS ---
st.divider()
st.subheader("📝 Adicionar Gastos Avulsos")
c1, c2, c3 = st.columns([2, 1, 1])
with c1: desc_extra = st.text_input("Descrição do gasto")
with c2: valor_extra = st.number_input("Valor (R$)", min_value=0.0, step=1.0)
with c3:
    st.write("###")
    if st.button("Adicionar"):
        if desc_extra and valor_extra > 0:
            st.session_state.dados["gastos_avulsos"].append({"desc": desc_extra, "valor": valor_extra})
            st.rerun()

# --- CÁLCULOS INTEGRADOS ---
gastos_variaveis_total = compras_mes + combustivel_carro + combustivel_moto
contas_fixas_total = financiamento + condominio + iptu + seguro_residencial + claro_tv_internet + luz + celular
lista_extras = st.session_state.dados.get("gastos_avulsos", [])
total_extras = sum(item['valor'] for item in lista_extras)

renda_total = adiantamento + salario_oficial
valor_guardar = renda_total * (porcentagem_guardar / 100)
saldo_livre = renda_total - valor_guardar - contas_fixas_total - gastos_variaveis_total - total_extras

# --- RESULTADOS ---
st.divider()
st.subheader("📊 Resumo Financeiro")
st.success(f"### Saldo Livre: R$ {saldo_livre:,.2f}")

if lista_extras:
    st.write("#### Gastos Avulsos Registrados:")
    st.table(pd.DataFrame(lista_extras))
    if st.button("Limpar extras"):
        st.session_state.dados["gastos_avulsos"] = []
        st.rerun()

# --- BOTÃO SALVAR ---
if st.button("Salvar Tudo como Padrão", type="primary"):
    # Atualiza o dicionário com os novos valores dos inputs
    st.session_state.dados.update({
        "adiantamento": adiantamento, "salario_oficial": salario_oficial,
        "porcentagem_guardar": porcentagem_guardar, "compras_mes": compras_mes,
        "combustivel_carro": combustivel_carro, "combustivel_moto": combustivel_moto,
        "financiamento": financiamento, "condominio": condominio, "iptu": iptu,
        "seguro_residencial": seguro_residencial, "claro_tv_internet": claro_tv_internet,
        "luz": luz, "celular": celular
    })
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(st.session_state.dados, f, ensure_ascii=False, indent=4)
    st.success("Tudo salvo com sucesso!")

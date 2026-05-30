import streamlit as st
import pandas as pd
import json
import os

# Configuração da página
st.set_page_config(page_title="Gestão Financeira Mensal", page_icon="💰", layout="centered")

ARQUIVO_DADOS = "dados_mes.json"

# --- FUNÇÃO DE CARGA COM PROTEÇÃO ---
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
                # Garante que a estrutura nova exista em arquivos antigos
                if "gastos_avulsos" not in dados_salvos:
                    dados_salvos["gastos_avulsos"] = []
                for chave, valor in valores_padrao.items():
                    dados_salvos.setdefault(chave, valor)
                return dados_salvos
        except: return valores_padrao
    return valores_padrao

# Inicialização
if "dados" not in st.session_state:
    st.session_state.dados = carregar_dados()

st.title("💰 Gestão de Salário & Planejamento Mensal")

# --- INPUTS (Exemplos simplificados - mantenha seus campos originais aqui) ---
adiantamento = st.number_input("Adiantamento", value=st.session_state.dados["adiantamento"])
salario_oficial = st.number_input("Pagamento Oficial", value=st.session_state.dados["salario_oficial"])

# --- GASTOS AVULSOS ---
st.subheader("📝 Adicionar Gastos Avulsos")
col_desc, col_valor, col_btn = st.columns([2, 1, 1])
with col_desc: descricao = st.text_input("Descrição")
with col_valor: valor_extra = st.number_input("Valor (R$)", min_value=0.0, step=1.0)
with col_btn:
    st.write("###")
    if st.button("Adicionar"):
        if descricao and valor_extra > 0:
            st.session_state.dados["gastos_avulsos"].append({"desc": descricao, "valor": valor_extra})
            st.rerun()

# --- CÁLCULOS SEGUROS ---
renda_total = adiantamento + salario_oficial
# Uso do .get para evitar o erro de KeyError
lista_extras = st.session_state.dados.get("gastos_avulsos", [])
total_extras = sum(item['valor'] for item in lista_extras)

# (Aqui você mantém seus outros cálculos de fixas/variáveis)
saldo_livre = renda_total - total_extras # Subtraindo apenas os extras como exemplo

st.success(f"### Saldo Livre: R$ {saldo_livre:,.2f}")

if lista_extras:
    st.write("#### Histórico de Gastos Avulsos:")
    st.table(pd.DataFrame(lista_extras))
    if st.button("Limpar extras"):
        st.session_state.dados["gastos_avulsos"] = []
        st.rerun()

# --- BOTÃO SALVAR ---
if st.button("Salvar Tudo como Padrão", type="primary"):
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(st.session_state.dados, f, ensure_ascii=False, indent=4)
    st.success("Dados salvos no servidor!")

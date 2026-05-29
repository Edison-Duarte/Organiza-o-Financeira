# --- NOVA SEÇÃO: RELATÓRIO DE GASTOS REAIS ---
st.divider()
st.subheader("📈 Acompanhamento dos Gastos Reais")

try:
    # Lê os dados da aba 'Lancamentos'
    df_lancamentos = conn.read(worksheet="Lancamentos", ttl="0d")
    
    if df_lancamentos is not None and not df_lancamentos.empty:
        # Converter coluna de data para datetime para garantir o filtro
        df_lancamentos["Data"] = pd.to_datetime(df_lancamentos["Data"])
        
        # Agrupa por categoria
        gastos_por_categoria = df_lancamentos.groupby("Categoria")["Valor"].sum().reset_index()
        
        # Exibe um gráfico simples
        st.bar_chart(gastos_por_categoria.set_index("Categoria"))
        
        # Exibe tabela detalhada
        st.write("Detalhamento por categoria:")
        st.dataframe(gastos_por_categoria, hide_index=True, use_container_width=True)
        
        # Comparativo com o orçamento (Projeção vs Real)
        total_gasto = df_lancamentos["Valor"].sum()
        st.metric("Total gasto no mês (Real)", f"R$ {total_gasto:,.2f}")
        
    else:
        st.info("Nenhum lançamento registrado este mês ainda.")
except Exception as e:
    st.warning("Ainda não há dados de lançamentos para exibir ou a aba 'Lancamentos' está vazia.")

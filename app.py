import streamlit as st
import pandas as pd
from io import StringIO
from utils.calculos import calcular_resultado
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

st.set_page_config(page_title="Desempenho dos Advogados", layout="wide")
st.title("📊 Dashboard Financeiro - Escritório de Advocacia")

# Estados para armazenar dados temporários
if 'advogados_lista' not in st.session_state:
    st.session_state.advogados_lista = []
if 'processos_lista' not in st.session_state:
    st.session_state.processos_lista = []

# Escolha de modo de entrada
modo = st.radio("Como você deseja inserir os dados?", ["📁 Upload de arquivos", "✍️ Cadastro manual"])

# Inicializa os DataFrames
df_adv = pd.DataFrame()
df_proc = pd.DataFrame()
total_custo_fixo = 0
qtd_rateio = 1

# -------------------
# 📁 Modo de Upload
# -------------------
if modo == "📁 Upload de arquivos":
    with st.expander("📥 Enviar arquivos CSV"):
        advogados = st.file_uploader("📁 Envie o arquivo de advogados", type=["csv"])
        processos = st.file_uploader("📁 Envie o arquivo de processos", type=["csv"])
        custo_manual = st.number_input("🏢 Informe o valor total de custo fixo anual (R$)", min_value=0.0, format="%.2f")
        rateio_manual = st.number_input("👥 Número total de pessoas para rateio", min_value=1, step=1)

        if advogados and processos:
            df_adv = pd.read_csv(advogados)
            df_proc = pd.read_csv(processos)
            total_custo_fixo = custo_manual
            qtd_rateio = rateio_manual

# -------------------
# ✍️ Modo Manual
# -------------------
elif modo == "✍️ Cadastro manual":
    with st.expander("✍️ Cadastro manual de dados"):
        st.markdown("Cadastre abaixo os advogados e processos diretamente no sistema.")

        # Advogado
        st.subheader("👥 Cadastrar Advogado")
        with st.form("form_advogado"):
            advogado_id = st.text_input("OAB do Advogado", key=f"adv_id_{len(st.session_state.advogados_lista)}")
            nome = st.text_input("Nome", key=f"adv_nome_{len(st.session_state.advogados_lista)}")
            custo_direto = st.number_input("Custo direto anual (R$)", min_value=0.0, format="%.2f", key=f"adv_custo_{len(st.session_state.advogados_lista)}")
            submitted_adv = st.form_submit_button("Adicionar advogado")

        if submitted_adv:
            st.session_state.advogados_lista.append({
                "advogado_id": advogado_id,
                "nome": nome,
                "custo_direto_anual": custo_direto
            })
            st.rerun()

        # Processo
        st.subheader("⚖️ Cadastrar Processo")
        with st.form("form_processo"):
            processo_id = st.text_input("ID do Processo", key=f"proc_id_{len(st.session_state.processos_lista)}")
            valor_recebido = st.number_input("Valor recebido (R$)", min_value=0.0, format="%.2f", key=f"proc_valor_{len(st.session_state.processos_lista)}")

            opcoes_adv = {
                f"{adv['advogado_id']} - {adv['nome']}": adv["advogado_id"]
                for adv in st.session_state.advogados_lista
            }

            advogado_selecionado = st.selectbox(
                "Selecione o advogado responsável pelo processo",
                options=list(opcoes_adv.keys()),
                key=f"proc_adv_{len(st.session_state.processos_lista)}"
            )

            advogado_proc = opcoes_adv.get(advogado_selecionado, "")
            participacao = st.number_input("Participação (%)", min_value=0.0, max_value=100.0, format="%.2f", key=f"proc_part_{len(st.session_state.processos_lista)}")
            submitted_proc = st.form_submit_button("Adicionar processo")

        if submitted_proc:
            st.session_state.processos_lista.append({
                "processo_id": processo_id,
                "valor_recebido": valor_recebido,
                "advogado_id": advogado_proc,
                "participacao (%)": participacao
            })
            st.rerun()

        # Custos fixos
        st.subheader("🏢 Rateio de Custos Fixos")
        total_custo_fixo = st.number_input("Valor total de custo fixo anual (R$)", min_value=0.0, format="%.2f")
        qtd_rateio = st.number_input("Número total de pessoas para rateio", min_value=1, step=1)

# -------------------
# Edição dos dados
# -------------------
with st.expander("✍️ Editar Valores"):
    if st.session_state.advogados_lista:
        st.markdown("### ✏️ Editar Lista de Advogados")
        df_adv = st.data_editor(pd.DataFrame(st.session_state.advogados_lista), num_rows="dynamic")

    if st.session_state.processos_lista:
        st.markdown("### ✏️ Editar Lista de Processos")
        df_proc = st.data_editor(pd.DataFrame(st.session_state.processos_lista), num_rows="dynamic")

# Visualização formatada
st.markdown("### 👁️ Visualização Formatada de Advogados")
if not df_adv.empty:
    df_adv_formatado = df_adv.copy()
    df_adv_formatado["custo_direto_anual"] = df_adv_formatado["custo_direto_anual"].apply(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )
    st.dataframe(df_adv_formatado)

st.markdown("### 👁️ Visualização Formatada de Processos")
if not df_proc.empty:
    df_proc_formatado = df_proc.copy()
    df_proc_formatado["valor_recebido"] = df_proc_formatado["valor_recebido"].apply(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )
    st.dataframe(df_proc_formatado)

# -------------------
# Explicação dos Cálculos
# -------------------
with st.expander("ℹ️ Como o resultado é calculado?"):
    st.markdown("""
    **Metodologia do Cálculo:**

    1. **Receita atribuída ao advogado**:
       - Cada processo possui um valor recebido pelo escritório.
       - Esse valor é distribuído entre os advogados conforme o percentual de participação informado.

    2. **Custo direto**:
       - É o total pago ao advogado no ano (ex: salário ou honorário fixo).

    3. **Custo fixo rateado**:
       - Valor informado manualmente, dividido igualmente entre o número de pessoas definidas para rateio.

    4. **Resultado líquido por advogado**:
       - Calculado como: `Receita atribuída - (Custo direto + Custo fixo rateado)`
    """)

# -------------------
# Resultado sob comando
# -------------------
if not df_adv.empty and not df_proc.empty and total_custo_fixo > 0:
    if st.button("📊 Calcular Resultado Financeiro"):
        resultado_df = calcular_resultado(df_adv, df_proc, total_custo_fixo, qtd_rateio)
        st.session_state.resultado_df = resultado_df

    if "resultado_df" in st.session_state:
        resultado_df = st.session_state.resultado_df

        st.subheader("📄 Resultado por Advogado")

        resultado_formatado = resultado_df.copy()
        for col in ["receita_advogado", "custo_direto_anual", "custo_fixo_rateado", "resultado_liquido"]:
            resultado_formatado[col] = resultado_formatado[col].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        st.dataframe(resultado_formatado)

        with st.expander("📈 Visualização Gráfica", expanded=True):
            nomes_adv = resultado_df["nome"].unique().tolist()
            adv_selecionado = st.selectbox("Selecione um advogado", nomes_adv, key="graf_adv")

            dados_adv = resultado_df[resultado_df["nome"] == adv_selecionado].iloc[0]

            labels = ["Receita", "Custo Direto", "Custo Fixo", "Resultado"]
            valores = [
                dados_adv["receita_advogado"],
                -dados_adv["custo_direto_anual"],
                -dados_adv["custo_fixo_rateado"],
                dados_adv["resultado_liquido"]
            ]
            cores = ["green", "red", "orange", "black"]

            fig, ax = plt.subplots(figsize=(8, 5))
            ax.bar(labels, valores, color=cores)

            ax.yaxis.set_major_formatter(mtick.FuncFormatter(
                lambda x, _: f'R$ {x:,.0f}'.replace(",", "X").replace(".", ",").replace("X", ".")
            ))
            ax.set_title(f"🔍 Resumo Financeiro - {adv_selecionado}")
            ax.axhline(0, color='gray', linewidth=0.8)
            st.pyplot(fig)
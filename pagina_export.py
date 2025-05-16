import streamlit as st
import pandas as pd

def exportar_lembretes(cursor):
    st.markdown("<h2>Exportar lembretes - Gestão da Tecnologia da Informação</h2>", unsafe_allow_html=True)

    user_role = st.session_state.get("role", "")
    if user_role != "admin":
        st.warning("Apenas administradores podem acessar esta página.")
        return

    cursor.execute("SELECT * FROM public.lembrete_tb")
    colnames = [desc[0] for desc in cursor.description]
    dados = cursor.fetchall()

    if not dados:
        st.info("Nenhum lembrete encontrado no banco de dados.")
        return

    df = pd.DataFrame(dados, columns=colnames)
    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📄 Baixar todos os lembretes em CSV",
        data=csv,
        file_name="lembretes.csv",
        mime="text/csv"
    )

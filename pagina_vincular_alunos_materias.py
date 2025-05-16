import streamlit as st
from datetime import datetime

def vincular_alunos_materia(cursor, conn):
    st.subheader("👥 Vincular Alunos a uma Matéria - Gestão da Tecnologia da Informação")

    # Selecionar matéria
    cursor.execute("SELECT materia_id, nome FROM public.materia_tb ORDER BY nome")
    materias = cursor.fetchall()
    mapa_materias = {f"{nome} (ID: {mid})": mid for mid, nome in materias}

    materia_selecionada = st.selectbox("Escolha a Matéria", ["Selecione..."] + list(mapa_materias.keys()))

    if materia_selecionada != "Selecione...":
        materia_id = mapa_materias[materia_selecionada]

        # Listar alunos disponíveis
        cursor.execute("SELECT aluno_id, nome FROM public.aluno_tb ORDER BY nome")
        alunos = cursor.fetchall()
        mapa_alunos = {f"{nome} (ID: {aid})": aid for aid, nome in alunos}

        alunos_selecionados = st.multiselect("Selecione os Alunos para adicionar", list(mapa_alunos.keys()))

        if st.button("➕ Adicionar Alunos à Matéria"):
            adicionados = 0
            for aluno_nome in alunos_selecionados:
                aluno_id = mapa_alunos[aluno_nome]
                # Verifica se já existe vínculo
                cursor.execute("SELECT 1 FROM public.aluno_materia_tb WHERE aluno_id = %s AND materia_id = %s", (aluno_id, materia_id))
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO public.aluno_materia_tb (aluno_id, materia_id, data_inclusao)
                        VALUES (%s, %s, %s)
                    """, (aluno_id, materia_id, datetime.now()))
                    adicionados += 1

            conn.commit()
            st.success(f"{adicionados} aluno(s) adicionados à matéria com sucesso.")

    st.markdown("---")
    st.subheader("📋 Visualizar Alunos por Matéria")

    for nome_materia, mid in mapa_materias.items():
        with st.expander(f"📘 {nome_materia}"):
            cursor.execute("""
                SELECT am.aluno_materia_id, a.nome
                FROM public.aluno_materia_tb am
                JOIN public.aluno_tb a ON am.aluno_id = a.aluno_id
                WHERE am.materia_id = %s
                ORDER BY a.nome
            """, (mid,))
            alunos_materia = cursor.fetchall()
            if alunos_materia:
                for am_id, aluno_nome in alunos_materia:
                    col1, col2 = st.columns([4, 1])
                    col1.markdown(f"- {aluno_nome}")
                    with col2:
                        if st.button("🗑️ Remover", key=f"remover_{am_id}"):
                            if st.confirm(f"Deseja remover {aluno_nome} desta matéria?"):
                              cursor.execute("DELETE FROM public.aluno_materia_tb WHERE aluno_materia_id = %s", (am_id,))
                              conn.commit()
                              st.success(f"Aluno {aluno_nome} removido da matéria.")
                              st.experimental_rerun()
            else:
                st.info("Nenhum aluno vinculado.")

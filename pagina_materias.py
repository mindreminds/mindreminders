import streamlit as st
from datetime import date

def badge(text, color):
    return f"<span style='background:{color}; color:white; padding:3px 8px; border-radius:8px; font-size:11px;'>{text}</span>"

def gerenciar_materias(cursor, conn):
    st.subheader("🏫 Adicionar Nova Matéria - Gestão da Tecnologia da Informação")

    cursor.execute("SELECT professor_id, nome FROM public.professor_tb ORDER BY nome")
    professores = cursor.fetchall()
    mapa_professores = {f"{nome} (ID: {pid})": pid for pid, nome in professores}

    nome_turma = st.text_input("Nome da Matéria")
    professor_nome = st.selectbox("Professor Responsável", ["Selecione..."] + list(mapa_professores.keys()))

    if st.button("➕ Criar Matéria"):
        if not nome_turma.strip() or professor_nome == "Selecione...":
            st.warning("Preencha todos os campos.")
        else:
            professor_id = mapa_professores[professor_nome]
            cursor.execute("""
                INSERT INTO public.materia_tb (nome, professor_id)
                VALUES (%s, %s)
            """, (nome_turma.strip(), professor_id))
            conn.commit()
            st.success("Matéria criada com sucesso!")
            st.experimental_rerun()

    st.markdown("---")
    st.subheader("📚 Matérias Cadastradas")

    cursor.execute("""
        SELECT t.materia_id, t.nome, p.nome as professor
        FROM public.materia_tb t
        LEFT JOIN public.professor_tb p ON t.professor_id = p.professor_id
        ORDER BY t.nome
    """)
    turmas = cursor.fetchall()

    for turma_id, nome, professor in turmas:
        with st.container():
            st.markdown(
                f"""
                <div style='border:1px solid #ccc; padding:10px; border-radius:10px; margin-bottom:10px;'>
                    <b>Matéria:</b> {nome}<br>
                    <b>Professor:</b> {professor or 'Sem professor'}
                </div>
                """, unsafe_allow_html=True
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button("✏️ Editar", key=f"editar_turma_{turma_id}"):
                    st.session_state.turma_a_editar = turma_id

            with col2:
                if st.button("🗑️ Excluir", key=f"excluir_turma_{turma_id}"):
                    cursor.execute("DELETE FROM public.materia_tb WHERE materia_id = %s", (turma_id,))
                    conn.commit()
                    st.success("Matéria excluída com sucesso.")
                    st.experimental_rerun()

    if "turma_a_editar" in st.session_state:
        turma_id = st.session_state.turma_a_editar
        st.markdown("---")
        st.subheader("✏️ Editar Matéria")

        cursor.execute("SELECT nome, professor_id FROM public.materia_tb WHERE materia_id = %s", (turma_id,))
        turma = cursor.fetchone()
        if turma:
            nome_atual, prof_atual_id = turma
            novo_nome = st.text_input("Novo Nome da Matéria", value=nome_atual)

            professores_options = ["Selecione..."] + list(mapa_professores.keys())
            professor_atual_nome = next((k for k, v in mapa_professores.items() if v == prof_atual_id), "Selecione...")
            novo_professor_nome = st.selectbox("Novo Professor", professores_options, index=professores_options.index(professor_atual_nome))

            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Salvar alterações"):
                    if novo_nome.strip() and novo_professor_nome != "Selecione...":
                        novo_professor_id = mapa_professores[novo_professor_nome]
                        cursor.execute("""
                            UPDATE public.materia_tb SET nome = %s, professor_id = %s WHERE materia_id = %s
                        """, (novo_nome.strip(), novo_professor_id, turma_id))
                        conn.commit()
                        st.success("Matéria atualizada com sucesso!")
                        del st.session_state.turma_a_editar
                        st.experimental_rerun()
            with col2:
                if st.button("❌ Cancelar edição"):
                    del st.session_state.turma_a_editar

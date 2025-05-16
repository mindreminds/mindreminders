import streamlit as st
from datetime import datetime, timedelta

def criar_lembretes(cursor, conn, professor_id):
    st.subheader("📝 Criar Lembrete para uma Matéria - Gestão da Tecnologia da Informação")

    # Buscar matérias do professor
    cursor.execute("""
        SELECT materia_id, nome FROM public.materia_tb
        WHERE professor_id = %s
        ORDER BY nome
    """, (professor_id,))
    materias = cursor.fetchall()
    mapa_materias = {f"{nome} (ID: {mid})": mid for mid, nome in materias}

    if not mapa_materias:
        st.info("Você ainda não possui matérias cadastradas.")
        return

    materia_nome = st.selectbox("Matéria", list(mapa_materias.keys()))
    tipo = st.selectbox("Tipo de lembrete", ["prova", "trabalho", "leitura", "exercício", "apresentação", "atividade online", "entrega parcial"])
    titulo = st.text_input("Título do lembrete")
    descricao = st.text_area("Descrição")
    data_entrega = st.date_input("Data de entrega", min_value=datetime.now().date())

    if st.button("💾 Criar Lembrete"):
        if not titulo.strip():
            st.warning("O título é obrigatório.")
            return

        materia_id = mapa_materias[materia_nome]

        cursor.execute("""
            INSERT INTO public.lembrete_tb (materia_id, professor_id, tipo, titulo, descricao, data_entrega)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING lembrete_id
        """, (materia_id, professor_id, tipo, titulo.strip(), descricao.strip(), data_entrega))
        lembrete_id = cursor.fetchone()[0]

        # Vincular todos os alunos da matéria
        cursor.execute("SELECT aluno_id FROM public.aluno_materia_tb WHERE materia_id = %s", (materia_id,))
        alunos = cursor.fetchall()
        for (aluno_id,) in alunos:
            cursor.execute("""
                INSERT INTO public.aluno_lembrete_tb (aluno_id, lembrete_id, status)
                VALUES (%s, %s, 'pendente')
            """, (aluno_id, lembrete_id))

        conn.commit()
        st.success("Lembrete criado e vinculado aos alunos com sucesso!")

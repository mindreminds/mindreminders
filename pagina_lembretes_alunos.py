import streamlit as st
from datetime import datetime

def gerenciar_lembretes_aluno(cursor, aluno_id):
    st.subheader("📌 Meus Lembretes - Gestão da Tecnologia da Informação")


    # Mapeamento para exibição
    status_map = {
        "Todos": None,
        "Pendente": "pendente",
        "Concluído": "concluído",
        "Atrasado": "atrasado",
        "Concluído com atraso": "concluído_atrasado" 
    }


    # Exibe os rótulos amigáveis
    status_legivel = st.selectbox("Filtrar por status", list(status_map.keys()))

    # Recupera o valor técnico correspondente
    filtro_status = status_map[status_legivel]
    
    query = """
        SELECT al.aluno_lembrete_id, l.titulo, l.tipo, l.descricao, l.data_entrega, al.status, al.comentario, al.data_conclusao
        FROM public.aluno_lembrete_tb al
        JOIN public.lembrete_tb l ON al.lembrete_id = l.lembrete_id
        WHERE al.aluno_id = %s
    """

    params = [aluno_id]

    if filtro_status == "concluído":
        query += " AND al.status = 'concluído'"
    elif filtro_status == "pendente":
        query += " AND al.status = 'pendente' AND l.data_entrega >= CURRENT_DATE"
    elif filtro_status == "atrasado":
        query += " AND al.status = 'pendente' AND l.data_entrega < CURRENT_DATE"
    elif filtro_status == "concluído_atrasado":  
        query += " AND al.status = 'concluído_atrasado'"
    query += " ORDER BY l.data_entrega ASC"

    cursor.execute(query, params)
    lembretes = cursor.fetchall()

    if not lembretes:
        st.info("Nenhum lembrete encontrado com esse filtro.")
        return

    for lembrete in lembretes:
        aluno_lembrete_id, titulo, tipo, descricao, data_entrega, status, comentario, data_conclusao = lembrete

        with st.expander(f"📘 {titulo} ({tipo}) - Entrega até {data_entrega.strftime('%d/%m/%Y')}"):
            st.markdown(f"**Descrição:** {descricao}")
            st.markdown(f"**Status atual:** `{status}`")

        if status == "pendente":
            novo_comentario = st.text_area("Adicionar comentário", value=comentario or "", key=f"coment_{aluno_lembrete_id}")
            if st.button("💾 Marcar como concluído", key=f"btn_{aluno_lembrete_id}"):
                data_entrega_date = data_entrega.date() if isinstance(data_entrega, datetime) else data_entrega
                status_final = "concluído_atrasado" if data_entrega_date < datetime.now().date() else "concluído"
                cursor.execute("""
                    UPDATE public.aluno_lembrete_tb
                    SET status = %s, comentario = %s, data_conclusao = %s
                    WHERE aluno_lembrete_id = %s
                """, (status_final, novo_comentario.strip(), datetime.now(), aluno_lembrete_id))
                cursor.connection.commit()
                st.success("Lembrete concluído!" if status_final == "concluído" else "Concluído com atraso!")
                st.experimental_rerun()
            else:
                st.markdown(f"**Comentário enviado:** {comentario or '-'}")
                st.markdown(f"**Concluído em:** {data_conclusao.strftime('%d/%m/%Y %H:%M')}" if data_conclusao else "-")

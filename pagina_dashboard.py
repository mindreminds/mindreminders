import streamlit as st
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
from datetime import datetime
import pandas as pd
import plotly.express as px

def gerar_dashboard(cursor):
    st.markdown("<h2 style='text-align:center;'>📊 Visão Geral dos Meus Lembretes - Gestão da Tecnologia da Informação</h2>", unsafe_allow_html=True)

    aluno_id = st.session_state.get("aluno_id")
    if not aluno_id:
        st.warning("Aluno não autenticado.")
        return

    # Filtros
    st.sidebar.markdown("### Filtros do Dashboard")
    filtro_status = st.sidebar.multiselect("Filtrar por status", ["pendente", "concluído", "atrasado"], default=["pendente", "concluído", "atrasado"])
    filtro_tipo = st.sidebar.text_input("Filtrar por tipo (ex: prova, trabalho)").strip().lower()

    query = """
        SELECT al.status,
               l.tipo,
               l.data_entrega,
               m.nome as materia
        FROM public.aluno_lembrete_tb al
        JOIN public.lembrete_tb l ON al.lembrete_id = l.lembrete_id
        JOIN public.materia_tb m ON l.materia_id = m.materia_id
        WHERE al.aluno_id = %s
    """

    cursor.execute(query, (aluno_id,))
    resultados = cursor.fetchall()

    if not resultados:
        st.info("Você ainda não possui lembretes.")
        return

    hoje = datetime.now().date()
    dados = []
    for status, tipo, data_entrega, materia in resultados:
        data_entrega_date = data_entrega.date() if isinstance(data_entrega, datetime) else data_entrega
        status_real = "atrasado" if status == "pendente" and data_entrega_date < hoje else status
        if status_real in filtro_status and (not filtro_tipo or filtro_tipo in tipo.lower()):
            dados.append((status_real, tipo, data_entrega, materia))

    if not dados:
        st.warning("Nenhum lembrete encontrado com os filtros selecionados.")
        return

    # Gráfico de Pizza por status
    contagem = Counter([s for s, _, _, _ in dados])
    labels = [s.capitalize() for s in contagem.keys()]
    valores = list(contagem.values())
    cores = ["#ffc107" if s == "pendente" else "#28a745" if s == "concluído" else "#dc3545" for s in contagem.keys()]

    fig1, ax1 = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax1.pie(
        valores,
        labels=None,
        colors=cores,
        autopct=lambda pct: f"{pct:.1f}% ({int(round(pct/100.*sum(valores)))})",
        startangle=90,
        wedgeprops=dict(width=0.4, edgecolor='white'),
        textprops=dict(color="black", fontsize=12),
        pctdistance=1.2
    )
    ax1.axis("equal")
    ax1.legend(wedges, labels, title="Status", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    st.pyplot(fig1)

    # Gráfico de Barras por Tipo
    st.markdown("### 📘 Distribuição por Tipo de Lembrete")
    tipos = [tipo for _, tipo, _, _ in dados]
    tipo_counts = Counter(tipos)
    fig2, ax2 = plt.subplots()
    ax2.bar(tipo_counts.keys(), tipo_counts.values(), color="#4a90e2")
    ax2.legend().remove() if ax2.get_legend() else None    
    st.pyplot(fig2)

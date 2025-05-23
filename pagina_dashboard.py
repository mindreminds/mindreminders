import streamlit as st
from collections import Counter, defaultdict
from datetime import datetime
import altair as alt
import pandas as pd

def gerar_dashboard(cursor):
    st.markdown("<h2 style='text-align:center;'>📊 Visão Geral dos Meus Lembretes - Gestão da Tecnologia da Informação</h2>", unsafe_allow_html=True)

    aluno_id = st.session_state.get("aluno_id")
    if not aluno_id:
        st.warning("Aluno não autenticado.")
        return

    # Filtros
    # Mapeamento rótulo legível → valor técnico
    status_opcoes = {
        "Pendente": "pendente",
        "Concluído": "concluído",
        "Atrasado": "atrasado",
        "Concluído com atraso": "concluído_atrasado"
    }

    st.sidebar.markdown("### Filtros do Dashboard")

    # Filtro com rótulos legíveis
    status_legivel = st.sidebar.multiselect(
        "Filtrar por status",
        list(status_opcoes.keys()),
        default=list(status_opcoes.keys())
    )

    # Converter para os valores técnicos
    filtro_status = [status_opcoes[s] for s in status_legivel]

    # Filtro por tipo (sem mudanças)
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

    # Preparar dados para Altair
    contagem = Counter([s for s, _, _, _ in dados])
    df_status = pd.DataFrame(contagem.items(), columns=["status", "total"])
    df_status['status_formatado'] = df_status['status'].map({
        "pendente": "Pendente",
        "concluído": "Concluído",
        "atrasado": "Atrasado",
        "concluído_atrasado": "Concluído com atraso"
    })
    df_status['percentual'] = df_status['total'] / df_status['total'].sum() * 100
    df_status['label'] = df_status.apply(lambda row: f"{row['percentual']:.1f}% ({row['total']})", axis=1)

    # Cores
    cores_status = {
        "pendente": "#ffc107",
        "concluído": "#28a745",
        "atrasado": "#dc3545",
        "concluído_atrasado": "#ff5733"
    }
    df_status['cor'] = df_status['status'].map(cores_status)

    # Gráfico principal
    chart = alt.Chart(df_status).mark_arc(innerRadius=60).encode(
        theta=alt.Theta(field="total", type="quantitative"),
        color=alt.Color(
            "status_formatado:N",
            scale=alt.Scale(range=df_status['cor'].tolist()),
            legend=alt.Legend(
                title="Status",
                orient="right",
                direction="horizontal",
                columns=2
            )
        ),
        tooltip=[
            alt.Tooltip("status_formatado:N", title="Status"),
            alt.Tooltip("total:Q", title="Total"),
            alt.Tooltip("percentual:Q", title="%", format=".1f")
        ]
    ).properties(height=600)

    st.altair_chart(chart, use_container_width=True)

    st.markdown("### 📘 Distribuição por Tipo de Lembrete")

    # Dados de tipos
    tipos = [tipo for _, tipo, _, _ in dados]
    tipo_counts = Counter(tipos)
    df_tipos = pd.DataFrame(tipo_counts.items(), columns=["tipo", "total"])

    # Ordenar por total
    df_tipos = df_tipos.sort_values(by="total", ascending=False)
    df_tipos['total_formatado'] = df_tipos['total'].apply(lambda x: f'{x / 1_000_000:.1f}M'.replace('.', ',') if x >= 1_000_000 else str(x))
    df_tipos['tipo'] = pd.Categorical(df_tipos['tipo'], categories=df_tipos['tipo'], ordered=True)

    # Gráfico
    chart = alt.Chart(df_tipos).mark_bar(color='#4a90e2').encode(
        x=alt.X('tipo:N', title='', sort=list(df_tipos['tipo'])),
        y=alt.Y(
            'total:Q',
            title='',
            axis=alt.Axis(labelExpr="datum.value >= 1000000 ? (datum.value / 1000000) + 'M' : datum.value"),
            scale=alt.Scale(domain=[0, df_tipos['total'].max() * 1.1])
        ),
        tooltip=[
            alt.Tooltip('tipo:N', title='Tipo'),
            alt.Tooltip('total:Q', title='Total de Lembretes', format=',')
        ]
    ).properties(height=600)

    # Texto acima das barras
    text = chart.mark_text(
        align='center',
        baseline='bottom',
        dy=-4,
        color='black'
    ).encode(
        text='total_formatado:N'
    )

    # Exibir no Streamlit
    st.altair_chart(chart + text, use_container_width=True)


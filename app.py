import streamlit as st
import pytz

from PIL import Image
from streamlit_option_menu import option_menu

from utils.conectaBanco import conectaBanco

from pagina_login import login, is_authenticated
from pagina_usuarios import gerenciar_usuarios
from pagina_trocarSenha import trocar_senha
from pagina_dashboard import gerar_dashboard
from pagina_export import exportar_lembretes
from pagina_materias import gerenciar_materias
from pagina_vincular_alunos_materias import vincular_alunos_materia
from pagina_criar_lembretes import criar_lembretes
from pagina_lembretes_alunos import gerenciar_lembretes_aluno


# Definir o timezone do Brasil
timezone_brasil = pytz.timezone('America/Sao_Paulo')

# Verifica a role do usuário logado
user_role = st.session_state.get('role', '')
user_name = st.session_state.get('nome', '')
user_area = st.session_state.get('area', '')

# Carregar credenciais do banco de dados
db_user = st.secrets["database"]["user"]
db_password = st.secrets["database"]["password"]

# Conexão com o banco de dados
conn, cursor = conectaBanco(db_user, db_password)

# Verifica se o usuário está autenticado
if not is_authenticated():
    login(cursor)
    st.stop()
    
# Carregar logos
logo = Image.open("logo.png")

# Configurações da página com o logo
st.set_page_config(page_title="Mind Reminders", page_icon="Century_mini_logo-32x32.png", layout="wide")
# Filtros e seleção de período
with st.sidebar:
    st.image(logo, width=150)

    # Determinar opções do menu com base na role
    menu_options = []
    menu_icons = []

    if user_role == "admin":
        menu_options.append("Controle de usuários")
        menu_icons.append("person-plus")
        menu_options.append("Controle de Matérias")
        menu_icons.append("mortarboard")
        menu_options.append("Vincular Alunos para Matérias")
        menu_icons.append("person-plus")
        menu_options.append("Exportar Dados")
        menu_icons.append("file-earmark-arrow-down")
        
    if user_role == "professor":
        menu_options.append("Criar Lembretes")
        menu_icons.append("calendar-plus")

    if user_role == "aluno":
        menu_options.append("Dashboard")
        menu_icons.append("mortarboard")
        menu_options.append("Gerenciar Lembretes")
        menu_icons.append("calendar-plus")
        
    else:
        menu_options.append("Trocar Senha")
        menu_icons.append("key")
                
    # Configuração do menu dinâmico
    selected_tab = option_menu(
        menu_title="Menu Principal",
        options=menu_options,
        icons=menu_icons,
        menu_icon="list",
        default_index=0,
    )

# Aba de Dashboard
if selected_tab == "Dashboard":
    gerar_dashboard(cursor)

elif selected_tab == "Criar Lembretes":
    col1, col2 = st.columns([1, 3])

    with col1:
        st.image(logo, width=150)

    with col2:
        st.markdown("<h2></h2>", unsafe_allow_html=True)

    if user_role == "professor":
        criar_lembretes(cursor, conn, st.session_state.get("professor_id"))
    else:
        st.warning("Você não tem permissão para acessar esta aba.")

   
# Aba de Relatórios
elif selected_tab == "Trocar Senha":
        col1, col2 = st.columns([1, 3])

        with col1:
            st.image(logo, width=150)

        with col2:
                st.markdown("<h2></h2>", unsafe_allow_html=True)

        trocar_senha(cursor, conn)

# Aba de Relatórios
elif selected_tab == "Controle de usuários":
        col1, col2 = st.columns([1, 3])

        with col1:
            st.image(logo, width=150)

        with col2:
            st.markdown("<h2></h2>", unsafe_allow_html=True)
            
        if user_role in ["admin"]:
            gerenciar_usuarios(cursor, conn)
        else:
            st.warning("Você não tem permissão para acessar esta aba.")

# Aba de Turmas
elif selected_tab == "Controle de Matérias":
        col1, col2 = st.columns([1, 3])

        with col1:
            st.image(logo, width=150)

        with col2:
            st.markdown("<h2></h2>", unsafe_allow_html=True)
            
        if user_role in ["admin"]:
            gerenciar_materias(cursor, conn)
        else:
            st.warning("Você não tem permissão para acessar esta aba.")
            
# Aba de Alunos X Matérias
elif selected_tab == "Vincular Alunos para Matérias":
        col1, col2 = st.columns([1, 3])

        with col1:
            st.image(logo, width=150)

        with col2:
            st.markdown("<h2></h2>", unsafe_allow_html=True)
            
        if user_role in ["admin"]:
            vincular_alunos_materia(cursor, conn)
        else:
            st.warning("Você não tem permissão para acessar esta aba.")

# Aba de export    
elif selected_tab == "Exportar Dados":
    col1, col2 = st.columns([1, 3])

    with col1:
        st.image(logo, width=150)

    with col2:
        st.markdown("<h2></h2>", unsafe_allow_html=True)

    exportar_lembretes(cursor)

elif selected_tab == "Gerenciar Lembretes":
    col1, col2 = st.columns([1, 3]) 

    with col1:
        st.image(logo, width=150)

    with col2:
        st.markdown("<h2></h2>", unsafe_allow_html=True)

    gerenciar_lembretes_aluno(cursor, st.session_state.get("aluno_id"))
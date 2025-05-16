import streamlit as st
import bcrypt

# Função para autenticação
def login(cursor):
    st.set_page_config(page_title="Mind Reminders", page_icon="logo.png")
    st.image("logo.png", use_column_width=True)

    st.title("Login")

    login_form = st.form(key="login_form")
    username = login_form.text_input("Usuário")
    password = login_form.text_input("Senha", type="password")
    login_button = login_form.form_submit_button("Entrar")

    if login_button:
        cursor.execute('SELECT "username" FROM public.users_py LIMIT 1')
        cursor.execute('SELECT "username", "nome", "password", "role", "ativo" FROM public.users_py WHERE "username" = %s', (username,))
        user_data = cursor.fetchone()

        if user_data:
            db_username, nome, hashed_pw, role, ativo = user_data

            if not ativo:
                st.error("Usuário inativado. Contate o administrador.")
            elif bcrypt.checkpw(password.encode("utf-8"), hashed_pw.encode("utf-8")):
                st.session_state['logged_in'] = True
                st.session_state['username'] = db_username
                st.session_state['role'] = role
                st.session_state['nome'] = nome

            if role == "professor":
                cursor.execute("SELECT professor_id FROM public.professor_tb WHERE email = %s", (db_username,))
                prof = cursor.fetchone()
                if prof:
                    st.session_state['professor_id'] = prof[0]

            elif role == "aluno":
                cursor.execute("SELECT aluno_id FROM public.aluno_tb WHERE email = %s", (db_username,))
                aluno = cursor.fetchone()
                if aluno:
                    st.session_state['aluno_id'] = aluno[0]

                st.success(f"Bem-vindo, {db_username}!")
                st.experimental_rerun()
            else:
                st.error("Usuário ou senha incorretos.")
        else:
            st.error("Usuário ou senha incorretos.")

# Função para verificar se o usuário está autenticado
def is_authenticated():
    return st.session_state.get('logged_in', False)
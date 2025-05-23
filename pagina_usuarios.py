import streamlit as st
import bcrypt
from datetime import date

from utils.auxiliar import validar_email, gerar_senha_automatica
from utils.email_utils import gerar_email_institucional, enviar_resultado

def badge(text, color):
    return f"<span style='background:{color}; color:white; padding:3px 8px; border-radius:8px; font-size:11px;'>{text}</span>"

def criar_usuario(cursor, conn):
    st.subheader("➕ Adicionar Novo Usuário - Gestão da Tecnologia da Informação")

    role = st.selectbox("Função", ["admin", "aluno", "professor"])
    username = st.text_input("E-mail do Usuário")
    nome = st.text_input("Nome do Usuário")

    data_nascimento = telefone = matricula = especialidade = None

    if role == "aluno":
        data_nascimento = st.date_input("Data de Nascimento", min_value=date(1950, 1, 1), max_value=date.today())
        telefone = st.text_input("Telefone")
        matricula = st.text_input("Matrícula")

    elif role == "professor":
        especialidade = st.text_input("Especialidade")
        telefone = st.text_input("Telefone")
        matricula = st.text_input("Matrícula")

    if st.button("Adicionar Usuário"):
        if not validar_email(username):
            st.warning("O e-mail não é válido.")
            return

        cursor.execute('SELECT 1 FROM public.users_py WHERE username = %s', (username,))
        if cursor.fetchone():
            st.warning("O e-mail já está em uso.")
            return

        senha_gerada = gerar_senha_automatica()
        hashed_password = bcrypt.hashpw(senha_gerada.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        cursor.execute("""
            INSERT INTO public.users_py (username, password, role, nome, ativo)
            VALUES (%s, %s, %s, %s, %s)
        """, (username, hashed_password, role, nome, True))

        if role == "aluno":
            cursor.execute("""
                INSERT INTO public.aluno_tb (nome, email, matricula, data_nascimento, telefone)
                VALUES (%s, %s, %s, %s, %s)
            """, (nome, username, matricula, data_nascimento, telefone))

        elif role == "professor":
            cursor.execute("""
                INSERT INTO public.professor_tb (nome, email, matricula, especialidade, telefone)
                VALUES (%s, %s, %s, %s, %s)
            """, (nome, username, matricula, especialidade, telefone))

        conn.commit()

        body = gerar_email_institucional("criar_usuario", {
            "nome": nome,
            "username": username,
            "senha": senha_gerada,
            "link_sistema": "https://mindreminders.streamlit.app/"
        })

        subject = "Seus dados de acesso - Mind Reminders"
        sender = st.secrets['smtp']['sender']
        recipient = username
        password = st.secrets['smtp']['password']

        enviar_resultado(subject, body, sender, [recipient], password, html=True)

        st.success(f"Usuário {username} criado e senha enviada por e-mail!")

def gerenciar_usuarios(cursor, conn):
    criar_usuario(cursor, conn)

    if "usuario_a_editar" not in st.session_state:
        st.session_state.usuario_a_editar = None

    st.markdown("<h2>👥 Gestão de Usuários</h2>", unsafe_allow_html=True)

    busca = st.text_input("🔎 Buscar usuário por nome ou e-mail").strip().lower()

    cursor.execute("SELECT username, nome, role, ativo FROM public.users_py ORDER BY nome")
    usuarios = cursor.fetchall()
    usuarios_filtrados = [
        dict(zip(["username", "nome", "role", "ativo"], u))
        for u in usuarios
        if busca in u[0].lower() or busca in (u[1] or "").lower()
    ] if busca else [dict(zip(["username", "nome", "role", "ativo"], u)) for u in usuarios]

    st.markdown(f"**Total encontrados:** {len(usuarios_filtrados)}")
    st.markdown("---")
    st.subheader("📁 Lista de Usuários")

    for usuario in usuarios_filtrados:
        ativo = usuario.get("ativo", True)
        badge_status = badge("Ativo", "#28a745") if ativo else badge("Inativo", "#dc3545")
        badge_role = badge(usuario.get("role", "user").capitalize(), "#007bff")

        with st.container():
            st.markdown(
                f"""
                <div style='border:1px solid #ddd; border-radius:10px; padding:10px; margin-bottom:10px;'>
                    <b>Nome:</b> {usuario.get('nome', '')} <br>
                    <b>E-mail:</b> {usuario.get('username', '')} <br>
                    {badge_status} {badge_role}
                </div>
                """, unsafe_allow_html=True
            )

            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                if st.button("✏️ Editar", key=f"editar_{usuario['username']}"):
                    st.session_state.usuario_a_editar = usuario

            with col2:
                if st.button("🚩 Inativar" if ativo else "✅ Reativar", key=f"inativar_{usuario['username']}"):
                    cursor.execute('UPDATE public.users_py SET ativo = %s WHERE username = %s', (not ativo, usuario['username']))
                    conn.commit()
                    st.success("Status do usuário atualizado.")
                    st.experimental_rerun()

            with col3:
                if st.button("🔒 Resetar Senha", key=f"reset_{usuario['username']}"):
                    nova_senha = gerar_senha_automatica()
                    hashed_password = bcrypt.hashpw(nova_senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                    cursor.execute('UPDATE public.users_py SET password = %s WHERE username = %s', (hashed_password, usuario['username']))
                    conn.commit()

                    body = gerar_email_institucional("redefinir_senha", {
                        "nome": usuario.get("nome", ""),
                        "senha": nova_senha,
                        "link_sistema": "https://mindreminders.streamlit.app/"
                    })

                    subject = "🔒 Redefinição de senha - Mind Reminders"
                    sender = st.secrets['smtp']['sender']
                    recipient = usuario.get("username", "")
                    password_smtp = st.secrets['smtp']['password']

                    enviar_resultado(subject, body, sender, [recipient], password_smtp, html=True)
                    st.success("Senha redefinida e enviada por e-mail.")

    if not usuarios_filtrados:
        st.info("Nenhum usuário encontrado.")

    if st.session_state.usuario_a_editar:
        usuario = st.session_state.usuario_a_editar
        with st.expander(f"✏️ Editar usuário: {usuario.get('username', '')}", expanded=True):
            novo_nome = st.text_input("Nome", value=usuario.get("nome", ""))
            novo_email = st.text_input("E-mail", value=usuario.get("username", ""))
            nova_role = st.selectbox("Função", ["admin", "aluno", "professor"], index=["admin", "aluno", "professor"].index(usuario.get("role", "user")))

            if nova_role == "aluno":
                cursor.execute("SELECT matricula, telefone, data_nascimento FROM aluno_tb WHERE email = %s", (usuario['username'],))
                aluno_data = cursor.fetchone()
                if aluno_data:
                    matricula, telefone, data_nascimento = aluno_data
                else:
                    matricula, telefone, data_nascimento = "", "", None
                st.text_input("Matrícula", value=matricula, disabled=True)
                novo_telefone = st.text_input("Telefone", value=telefone or "")
                nova_data_nascimento = st.date_input("Data de Nascimento", value=data_nascimento or date.today())

            elif nova_role == "professor":
                cursor.execute("SELECT matricula, telefone, especialidade FROM professor_tb WHERE email = %s", (usuario['username'],))
                prof_data = cursor.fetchone()
                if prof_data:
                    matricula, telefone, especialidade = prof_data
                else:
                    matricula, telefone, especialidade = "", "", ""
                st.text_input("Matrícula", value=matricula, disabled=True)
                novo_telefone = st.text_input("Telefone", value=telefone or "")
                nova_especialidade = st.text_input("Especialidade", value=especialidade or "")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("📏 Salvar alterações"):
                    if not validar_email(novo_email):
                        st.warning("E-mail inválido.")
                    else:
                        cursor.execute('SELECT 1 FROM public.users_py WHERE username = %s AND username <> %s', (novo_email, usuario['username']))
                        if cursor.fetchone():
                            st.warning("Este e-mail já está em uso.")
                        else:
                            cursor.execute("""
                                UPDATE public.users_py
                                SET nome = %s, username = %s, role = %s
                                WHERE username = %s
                            """, (novo_nome.strip(), novo_email.strip(), nova_role, usuario['username']))

                            if nova_role == "aluno":
                                cursor.execute("""
                                    UPDATE aluno_tb SET
                                        nome = %s,
                                        telefone = %s,
                                        data_nascimento = %s,
                                        email = %s
                                    WHERE email = %s
                                """, (novo_nome.strip(), novo_telefone.strip(), nova_data_nascimento, novo_email.strip(), usuario['username']))

                            elif nova_role == "professor":
                                cursor.execute("""
                                    UPDATE professor_tb SET
                                        nome = %s,
                                        telefone = %s,
                                        especialidade = %s,
                                        email = %s
                                    WHERE email = %s
                                """, (novo_nome.strip(), novo_telefone.strip(), nova_especialidade.strip(), novo_email.strip(), usuario['username']))

                            conn.commit()
                            st.success("Usuário atualizado com sucesso!")
                            st.session_state.usuario_a_editar = None
                            st.experimental_rerun()

            with col2:
                if st.button("❌ Cancelar edição"):
                    st.session_state.usuario_a_editar = None

    st.markdown("---")

import streamlit as st
import bcrypt

from utils.auxiliar import validar_senha

# Função para troca de senha com PostgreSQL
def trocar_senha(cursor, conn):
    st.subheader("Trocar senha - Gestão da Tecnologia da Informação")

    username = st.session_state.get('username')

    if not username:
        st.error("Você precisa estar logado para trocar a senha.")
        return

    with st.form("form_trocar_senha"):
        st.write("Troca de Senha")
        senha_atual = st.text_input("Senha Atual", type="password")
        nova_senha = st.text_input("Nova Senha", type="password")
        confirmar_nova_senha = st.text_input("Confirmar Nova Senha", type="password")
        senha_valida = validar_senha(nova_senha) and nova_senha == confirmar_nova_senha

        trocar_button = st.form_submit_button("Alterar Senha")

        if trocar_button:
            cursor.execute('SELECT password FROM public.users_py WHERE username = %s', (username,))
            result = cursor.fetchone()

            if result:
                hashed_senha_atual = result[0]

                if bcrypt.checkpw(senha_atual.encode("utf-8"), hashed_senha_atual.encode("utf-8")):
                    if senha_valida:
                        nova_senha_hash = bcrypt.hashpw(nova_senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
                        cursor.execute(
                            'UPDATE public.users_py SET password = %s WHERE username = %s',
                            (nova_senha_hash, username)
                        )
                        conn.commit()
                        st.success("Senha alterada com sucesso!")
                        st.session_state.mostrar_form_troca_senha = False
                    else:
                        if nova_senha != confirmar_nova_senha:
                            st.warning('As senhas não coincidem.')
                        elif not validar_senha(nova_senha):
                            st.warning('A senha deve conter no mínimo 8 caracteres e conter letra maiúscula, minúscula, número e caractere especial.')
                else:
                    st.error("A senha atual está incorreta.")
            else:
                st.error("Usuário não encontrado.")

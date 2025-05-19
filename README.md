# Mind Reminders – Sistema de Lembretes com Streamlit

Este projeto é um sistema de lembretes acadêmicos desenvolvido em [Streamlit](https://streamlit.io/), com autenticação por perfil, controle de usuários, professores, alunos, matérias e lembretes vinculados. Ideal para professores criarem lembretes e alunos gerenciarem prazos e entregas de atividades.

## Funcionalidades

### 👥 Autenticação de Usuários
- Login seguro com criptografia de senha (`bcrypt`)
- Perfis: `admin`, `professor`, `aluno`
- Redirecionamento de funcionalidades conforme perfil

### 🎓 Gestão Acadêmica
- Cadastro de professores e alunos
- Vinculação de alunos a matérias
- Cadastro e edição de matérias

### 📝 Lembretes (Professores)
- Criação de lembretes com título, tipo (prova, trabalho etc.), descrição e data de entrega
- Vinculação automática a todos os alunos da matéria selecionada

### 📌 Lembretes (Alunos)
- Visualização de todos os lembretes da sua turma
- Filtro por status: pendente, atrasado, concluído
- Possibilidade de adicionar comentário e marcar lembrete como concluído

### 🔐 Gestão de Usuários (Admin)
- Cadastro, inativação e edição de usuários
- Reset de senha com envio automático por e-mail

### ✉️ Notificações por E-mail
- Envio de senha e atualizações via SMTP
- Suporte para Mailtrap, Gmail, entre outros

---

## Tecnologias Utilizadas

- [Streamlit](https://streamlit.io/)
- [PostgreSQL](https://www.postgresql.org/)
- [Psycopg2](https://www.psycopg.org/)
- [Pytz](https://pytz.sourceforge.net/)
- [bcrypt](https://pypi.org/project/bcrypt/)
- [Pillow](https://pillow.readthedocs.io/)
- [Streamlit Option Menu](https://github.com/victoryhb/streamlit-option-menu)
- [smtplib](https://docs.python.org/3/library/smtplib.html)

---

## Estrutura do Projeto

```plaintext
.
├── app.py                        # Aplicação principal
├── pagina_login.py              # Autenticação
├── pagina_usuarios.py           # Gestão de usuários
├── pagina_trocarSenha.py        # Tela de troca de senha
├── pagina_dashboard.py          # Painel geral
├── pagina_export.py             # Exportação de dados
├── pagina_materias.py           # Cadastro de matérias
├── pagina_vincular_alunos_materias.py  # Vinculação alunos ↔ matérias
├── pagina_criar_lembretes.py    # Criação de lembretes (professor)
├── pagina_lembretes_alunos.py   # Visualização e conclusão de lembretes (aluno)
├── utils/
│   ├── conectaBanco.py          # Conexão com PostgreSQL
│   ├── auxiliar.py              # Validações e utilitários
│   └── email_utils.py           # Envio de e-mails
├── .streamlit/secrets.toml      # Credenciais (não subir para o Git)
├── requirements.txt             # Dependências
└── README.md                    # Documentação
```

---

## Configuração do Ambiente

1. **Clone o projeto**:
   ```bash
   git clone https://github.com/usuario/mind-reminders.git
   cd mind-reminders
   ```

2. **Crie e ative um ambiente virtual**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate # Mac/Linux
   ```

3. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure o arquivo `secrets.toml`**:
   ```toml
   [database]
   user = "postgres"
   password = "xxx"

   [smtp]
   sender = "sistema@mindreminders.com"
   password = "xxx"
   ```

5. **Execute o sistema**:
   ```bash
   streamlit run app.py
   ```

---

## Telas do Sistema

- Login (todos os perfis)
- Lembretes personalizados (aluno)
- Criação de lembretes (professor)
- Troca de Senha (admin/professor)
- Controle de Usuários (admin)
- Cadastro de Matérias (admin)
- Vincular Alunos a Matérias (admin)
- Exportar lembretes (admin)

---

## Licença

Este projeto é distribuído sob a licença MIT.

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def gerar_email_institucional(tipo, dados):
    link_sistema = dados.get("link_sistema", "https://mindreminders.streamlit.app/")

    header = f"""
    <div style='background-color:#004080; padding:20px; text-align:center;'>
    </div>
    """

    footer = """
    <div style='background:#f0f0f0; padding:10px; text-align:center; font-size:11px; color:#777;'>
        Este e-mail foi enviado automaticamente pelo sistema Mind Reminders.
    </div>
    """

    if tipo == "criar_usuario":
        body = f"""
        <h2 style='color:#004080;'>🚀 Sua conta foi criada</h2>
        <p>Olá <strong>{dados['nome']}</strong>,</p>
        <p>Seu acesso ao sistema Mind Reminders foi criado com sucesso!</p>
        <p><b>Usuário:</b> {dados['username']}<br>
        <b>Senha Provisória:</b> {dados['senha']}</p>
        <p style='font-size:13px; color:#666;'>Recomendamos trocar sua senha após o primeiro login.</p>
        <a href='{link_sistema}' style='display:inline-block; padding:10px 20px; background:#004080; color:#fff; text-decoration:none; border-radius:5px; margin-top:15px;'>Acessar o Sistema</a>
        """

    elif tipo == "redefinir_senha":
        body = f"""
        <h2 style='color:#004080;'>🔑 Redefinição de Senha</h2>
        <p>Olá <strong>{dados['nome']}</strong>,</p>
        <p>Conforme solicitado, sua senha foi redefinida.</p>
        <p><b>Nova Senha:</b> {dados['senha']}</p>
        <p>Por segurança, altere sua senha assim que possível.</p>
        <a href='{link_sistema}' style='display:inline-block; padding:10px 20px; background:#004080; color:#fff; text-decoration:none; border-radius:5px; margin-top:15px;'>Acessar o Sistema</a>
        """

    elif tipo == "notificacao":
        body = f"""
        <h2 style='color:#004080;'>🔔 Notificação</h2>
        <p>{dados['mensagem']}</p>
        <a href='{link_sistema}' style='display:inline-block; padding:10px 20px; background:#004080; color:#fff; text-decoration:none; border-radius:5px; margin-top:15px;'>Acessar o Sistema</a>
        """

    else:
        body = "<p>Tipo de e-mail inválido.</p>"

    return f"""
    <div style='font-family: Arial, sans-serif; max-width:600px; margin:auto; border:1px solid #e0e0e0; border-radius:8px; overflow:hidden; background:#ffffff;'>
        {header}
        <div style='padding:20px;'>{body}</div>
        {footer}
    </div>
    """
    
def enviar_resultado(subject, body, sender, recipients, password, html=False):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)

    part = MIMEText(body, "html" if html else "plain", "utf-8")
    msg.attach(part)

    smtp_host = "sandbox.smtp.mailtrap.io"
    smtp_port = 2525
    smtp_user = "c6f309805a8ed3"
    smtp_pass = password

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_user, smtp_pass)
        server.sendmail(sender, recipients, msg.as_string())


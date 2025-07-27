from flask_mail import Mail, Message
from flask import current_app, render_template
from .models import ConfigGlobal

mail = Mail()

# --- Função de setup de e-mail reutilizável ---
def setup_dynamic_mail():
    """Busca as configurações de SMTP do banco e prepara o objeto Mail."""
    temp_mail = Mail()
    temp_app = current_app._get_current_object()
    
    smtp_user = ConfigGlobal.get_setting('SMTP_USER')
    
    temp_app.config.update(
        MAIL_SERVER=ConfigGlobal.get_setting('SMTP_SERVER'),
        MAIL_PORT=int(ConfigGlobal.get_setting('SMTP_PORT', 587)),
        MAIL_USE_TLS=ConfigGlobal.get_setting('SMTP_USE_TLS', 'true').lower() == 'true',
        MAIL_USE_SSL=not (ConfigGlobal.get_setting('SMTP_USE_TLS', 'true').lower() == 'true'),
        MAIL_USERNAME=smtp_user,
        MAIL_PASSWORD=ConfigGlobal.get_setting('SMTP_PASSWORD'),
        MAIL_DEFAULT_SENDER=(ConfigGlobal.get_setting('COMPANY_NAME', 'CRM Azevix'), smtp_user)
    )
    temp_mail.init_app(temp_app)
    return temp_mail, temp_app

def send_test_email(smtp_settings, test_recipient):
    """Função para enviar um e-mail de teste com configurações dinâmicas."""
    temp_mail = Mail()
    temp_app = current_app._get_current_object()

    temp_app.config.update(
        MAIL_SERVER=smtp_settings.get('SMTP_SERVER'),
        MAIL_PORT=int(smtp_settings.get('SMTP_PORT')),
        MAIL_USE_TLS=smtp_settings.get('SMTP_USE_TLS'),
        MAIL_USE_SSL=not smtp_settings.get('SMTP_USE_TLS'),
        MAIL_USERNAME=smtp_settings.get('SMTP_USER'),
        MAIL_PASSWORD=smtp_settings.get('SMTP_PASSWORD'),
        MAIL_DEFAULT_SENDER=(ConfigGlobal.get_setting('COMPANY_NAME', 'CRM Azevix'), smtp_settings.get('SMTP_USER'))
    )
    temp_mail.init_app(temp_app)

    msg = Message(
        'E-mail de Teste - CRM Azevix',
        recipients=[test_recipient]
    )
    msg.body = 'Se você está recebendo este e-mail, suas configurações de SMTP estão funcionando corretamente!'

    with temp_app.app_context():
        temp_mail.send(msg)

# --- ADIÇÃO v7.1: Função para enviar e-mail de convite ---
def send_invitation_email(user, invitation_link):
    """Envia um e-mail de convite para um novo usuário."""
    temp_mail, temp_app = setup_dynamic_mail()
    company_name = ConfigGlobal.get_setting('COMPANY_NAME', 'CRM Azevix')
    
    msg = Message(
        f'Você foi convidado para o CRM {company_name}',
        recipients=[user.email]
    )
    # Usaremos um template HTML para o corpo do e-mail no futuro, por enquanto será texto simples.
    msg.body = f"""
    Olá, {user.name}!

    Você foi convidado para se juntar ao sistema CRM da empresa {company_name}.
    Para ativar sua conta e definir sua senha, por favor, acesse o link abaixo:
    {invitation_link}

    Este link é válido por 24 horas.

    Atenciosamente,
    Equipe {company_name}
    """
    
    with temp_app.app_context():
        temp_mail.send(msg)
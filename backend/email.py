from flask_mail import Mail, Message
from flask import current_app
from .models import ConfigGlobal

mail = Mail()

def send_test_email(app_config, smtp_server, smtp_port, smtp_user, smtp_password, smtp_use_tls, test_recipient):
    """Função para enviar um e-mail de teste com configurações dinâmicas."""
    # Configura uma instância temporária do Mail com os dados do formulário
    temp_mail = Mail()
    temp_app = current_app._get_current_object()
    
    temp_app.config.update(
        MAIL_SERVER=smtp_server,
        MAIL_PORT=smtp_port,
        MAIL_USE_TLS=smtp_use_tls,
        MAIL_USE_SSL=not smtp_use_tls,
        MAIL_USERNAME=smtp_user,
        MAIL_PASSWORD=smtp_password,
        MAIL_DEFAULT_SENDER=(ConfigGlobal.get_setting('COMPANY_NAME', 'CRM Azevix'), smtp_user)
    )
    temp_mail.init_app(temp_app)
    
    msg = Message(
        'E-mail de Teste - CRM Azevix',
        recipients=[test_recipient]
    )
    msg.body = 'Se você está recebendo este e-mail, suas configurações de SMTP estão funcionando corretamente!'
    
    with temp_app.app_context():
        temp_mail.send(msg)
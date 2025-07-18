from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os

db = SQLAlchemy()
login_manager = LoginManager()

def setup_database(app):
    """Cria as tabelas e popula os dados iniciais, como os papéis (Roles)."""
    with app.app_context():
        db.create_all()
        from .models import Role
        initial_roles = {
            'admin': 'Administrador do Sistema com acesso total.',
            'gerente': 'Líder de equipe com visão sobre seus liderados.',
            'vendedor': 'Usuário padrão que gerencia suas próprias contas.'
        }
        for role_name, role_description in initial_roles.items():
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                new_role = Role(name=role_name, description=role_description)
                db.session.add(new_role)
        db.session.commit()
        print("Tabelas e papéis essenciais verificados/criados.")

def create_app():
    load_dotenv()
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    if not app.config['SECRET_KEY']:
        raise ValueError("SECRET_KEY não configurada no arquivo .env!")

    DB_USER = os.getenv('POSTGRES_USER')
    DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    DB_NAME = os.getenv('POSTGRES_DB')
    DB_HOST = 'crm-azevix-db'
    DB_PORT = '5432'
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- Registro de Blueprints ---
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/')
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/')
    from .contas import contas as contas_blueprint
    app.register_blueprint(contas_blueprint, url_prefix='/')
    from .user import user as user_blueprint
    app.register_blueprint(user_blueprint, url_prefix='/')
    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)
    from .leads import leads as leads_blueprint
    app.register_blueprint(leads_blueprint)

    setup_database(app)

    return app
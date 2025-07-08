from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    load_dotenv()

    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'uma-chave-secreta-padrao-muito-segura')
    
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
    login_manager.login_message_category = "info"

    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- Registro de Blueprints (Módulos) ---
    # Garante que cada um seja registrado uma única vez.
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/')

    from .leads import leads as leads_blueprint
    app.register_blueprint(leads_blueprint, url_prefix='/')

    return app
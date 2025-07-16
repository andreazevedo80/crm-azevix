from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from .models import User

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.before_request
@login_required
def require_admin():
    """Garante que apenas usuários com a role 'admin' acessem este blueprint."""
    if not current_user.has_role('admin'):
        abort(403)

# --- ADIÇÃO v5.01: Rota para o dashboard administrativo ---
@admin.route('/')
def dashboard():
    """Página principal do painel de administração."""
    return render_template('admin/dashboard.html')

@admin.route('/users')
def user_management():
    """Página de listagem e gestão de usuários."""
    users = User.query.order_by(User.name).all()
    return render_template('admin/user_management.html', users=users)
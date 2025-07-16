from flask import Blueprint, render_template, abort, jsonify, request
from flask_login import login_required, current_user
from .models import User, Role, db

# --- ADIÇÃO v5.01: Novo Blueprint para o Painel de Administração ---
admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.before_request
@login_required
def require_admin():
    """Garante que apenas usuários com a role 'admin' acessem este blueprint."""
    if not current_user.has_role('admin'):
        abort(403)

@admin.route('/')
def dashboard():
    """Página principal do painel de administração."""
    return render_template('admin/dashboard.html')

@admin.route('/users')
def user_management():
    """Página de listagem e gestão de usuários."""
    users = User.query.order_by(User.name).all()
    return render_template('admin/user_management.html', users=users)

# --- ADIÇÃO v5.01: Novas rotas de API para gerenciar usuários ---

@admin.route('/api/users/<int:user_id>', methods=['GET'])
def get_user_details(user_id):
    """Busca os detalhes de um usuário para o modal de edição."""
    user = User.query.get_or_404(user_id)
    roles = Role.query.all()
    # Apenas gerentes e admins podem ser gerentes de outros
    potential_managers = User.query.join(User.roles).filter(Role.name.in_(['admin', 'gerente'])).all()
    
    user_data = {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'gerente_id': user.gerente_id,
        'roles': [role.id for role in user.roles]
    }
    
    return jsonify({
        'success': True,
        'user': user_data,
        'all_roles': [{'id': r.id, 'name': r.name} for r in roles],
        'all_managers': [{'id': m.id, 'name': m.name} for m in potential_managers]
    })

@admin.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Atualiza os dados de um usuário."""
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    
    gerente_id = data.get('gerente_id')
    user.gerente_id = int(gerente_id) if gerente_id else None
    
    # Atualiza os papéis (roles)
    role_ids = data.get('roles', [])
    user.roles = Role.query.filter(Role.id.in_(role_ids)).all()
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Usuário atualizado com sucesso!'})

@admin.route('/api/users/<int:user_id>/toggle-status', methods=['POST'])
def toggle_user_status(user_id):
    """Ativa ou desativa um usuário."""
    user = User.query.get_or_404(user_id)
    
    # Impede que o admin desative a si mesmo
    if user.id == current_user.id:
        return jsonify({'success': False, 'error': 'Você não pode desativar a si mesmo.'}), 403

    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({'success': True, 'message': f'Status do usuário {user.name} alterado.'})
from flask import Blueprint, render_template, abort, jsonify, request
from flask_login import login_required, current_user
from .models import User, Role, Conta, db

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

# --- ADIÇÃO v5.01.1: Rotas para Gestão de Contas ---
@admin.route('/accounts')
def account_management():
    """Página de listagem e gestão de contas."""
    return render_template('admin/account_management.html')

# --- ALTERAÇÃO v5.01.2: Adicionada lógica de busca e paginação ---
@admin.route('/api/accounts', methods=['GET'])
def get_all_accounts():
    """API que busca todas as contas, com filtro de status, busca e paginação."""
    page = request.args.get('page', 1, type=int)
    per_page = 15
    status = request.args.get('status', 'active')
    search = request.args.get('search', '').strip()

    query = Conta.query.filter_by(is_active=(status == 'active'))
    
    if search:
        query = query.filter(db.or_(
            Conta.nome_fantasia.ilike(f'%{search}%'),
            Conta.razao_social.ilike(f'%{search}%')
        ))

    pagination = query.order_by(Conta.nome_fantasia).paginate(page=page, per_page=per_page, error_out=False)
    contas = [c.to_dict() for c in pagination.items]
    
    return jsonify({
        'success': True,
        'contas': contas,
        'pagination': {
            'total': pagination.total,
            'pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next,
            'page': pagination.page
        }
    })


@admin.route('/api/accounts/<int:conta_id>/reactivate', methods=['POST'])
def reactivate_account(conta_id):
    """Reativa uma conta que foi desativada."""
    conta = Conta.query.get_or_404(conta_id)
    conta.is_active = True
    db.session.commit()
    return jsonify({'success': True, 'message': 'Conta reativada com sucesso.'})

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
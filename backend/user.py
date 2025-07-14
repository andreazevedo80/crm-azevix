from flask import Blueprint, render_template, request, jsonify, flash
from flask_login import login_required, current_user
from . import db

user = Blueprint('user', __name__)

@user.route('/perfil')
@login_required
def perfil():
    """Renderiza a página de perfil do usuário."""
    return render_template('user/perfil.html')

@user.route('/api/user/change-password', methods=['POST'])
@login_required
def change_password():
    """API para alterar a senha do usuário logado."""
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not current_password or not new_password:
        return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios.'}), 400

    if not current_user.check_password(current_password):
        return jsonify({'success': False, 'message': 'A senha atual está incorreta.'}), 403
    
    current_user.set_password(new_password)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Senha alterada com sucesso!'})
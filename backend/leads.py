from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from .models import Lead, User, db

leads = Blueprint('leads', __name__)

# --- ROTA DE PÁGINA ---
@leads.route('/leads')
@login_required
def listar_leads():
    """Renderiza a página principal de gestão de leads."""
    return render_template('leads/leads.html')

# --- ROTA DE API ---
@leads.route('/api/leads', methods=['GET'])
@login_required
def get_leads():
    """
    API para buscar e filtrar leads.
    Esta é a base que será expandida com a lógica de Lead Pool,
    filtros, paginação e permissões hierárquicas.
    """
    # Lógica de busca e permissão será adicionada aqui nos próximos passos
    
    # Por enquanto, retorna um resultado vazio paginado
    return jsonify({
        'success': True,
        'leads': [],
        'pagination': {
            'total': 0, 'pages': 0, 'has_prev': False,
            'has_next': False, 'page': 1
        }
    })
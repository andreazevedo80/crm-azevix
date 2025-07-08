from flask import Blueprint, render_template
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

@main.route('/')
@login_required # Agora o dashboard exige login
def dashboard():
    return render_template('dashboard.html', name=current_user.name)

# As rotas de leads (/leads, /novo-lead) virão para um blueprint 'leads.py' no futuro
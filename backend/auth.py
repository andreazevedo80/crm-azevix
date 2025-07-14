from flask import Blueprint, render_template, redirect, url_for, flash, request
from .models import User, Role, db
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if not user or not user.is_active or not user.check_password(password):
            flash('Email ou senha inválidos, ou conta inativa.', 'danger')
            return redirect(url_for('auth.login'))
        login_user(user)
        return redirect(url_for('main.dashboard'))
    return render_template('auth/login.html')

# --- ALTERAÇÃO: Lógica de 'Primeiro Usuário' implementada ---
@auth.route('/register', methods=['GET', 'POST'])
def register():
    # Se já existe algum usuário, desativa a rota de registro público
    if User.query.count() > 0:
        flash('O registro público está desativado. Por favor, solicite um convite.', 'info')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Este e-mail já está cadastrado.', 'warning')
            return redirect(url_for('auth.register'))

        new_user = User(email=email, name=name)
        new_user.set_password(password)
        new_user.is_active = True # O primeiro usuário já nasce ativo

        # --- Lógica para atribuir o papel de Admin ao primeiro usuário ---
        admin_role = Role.query.filter_by(name='admin').first()
        if admin_role:
            new_user.roles.append(admin_role)
        
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user, remember=True)
        flash('Conta de administrador criada com sucesso! Bem-vindo(a).', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('auth/register.html')

# --- ADIÇÃO: Rota para o usuário definir a senha via convite ---
@auth.route('/set-password/<token>', methods=['GET', 'POST'])
def set_password_with_token(token):
    user = User.query.filter_by(invitation_token=token).first()

    if not user or user.invitation_expiration < datetime.utcnow():
        flash('Link de convite inválido ou expirado. Peça um novo convite.', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        if not password or password != password_confirm or len(password) < 6:
            flash('As senhas não conferem ou são muito curtas.', 'warning')
            return render_template('auth/set_password.html', token=token)
        
        user.set_password(password)
        user.is_active = True
        user.invitation_token = None
        user.invitation_expiration = None
        db.session.commit()

        flash('Sua conta foi ativada com sucesso! Bem-vindo(a).', 'success')
        login_user(user)
        return redirect(url_for('main.dashboard'))

    return render_template('auth/set_password.html', token=token)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
from flask import Blueprint, render_template, abort, jsonify, request, current_app, url_for, Response
from flask_login import login_required, current_user
from .models import User, Role, Conta, db, ConfigGlobal, DominiosPermitidos, Lead, Contato, HistoricoImportacao
from .utils import encrypt_data, decrypt_data, is_valid_cnpj, get_cnpj_hash, normalize_name
from .email import send_test_email, send_invitation_email
import csv
import io
import json

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

@admin.route('/accounts')
def account_management():
    """Página de listagem e gestão de contas."""
    return render_template('admin/account_management.html')

# --- ALTERAÇÃO Adicionada lógica de busca e paginação ---
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

# --- Rota centralizada para dados de formulários de admin ---
@admin.route('/api/admin/form_data', methods=['GET'])
def get_admin_form_data():
    """Busca todos os dados necessários para os formulários de gestão (roles, gerentes, etc.)."""
    roles = Role.query.order_by(Role.name).all()
    potential_managers = User.query.join(User.roles).filter(Role.name.in_(['admin', 'gerente']), User.is_active==True).order_by(User.name).all()
    
    return jsonify({
        'success': True,
        'all_roles': [{'id': r.id, 'name': r.name} for r in roles],
        'all_managers': [{'id': m.id, 'name': m.name} for m in potential_managers]
    })

@admin.route('/api/users/<int:user_id>', methods=['GET'])
def get_user_details(user_id):
    user = User.query.get_or_404(user_id)
    roles = Role.query.all()
    potential_managers = User.query.join(User.roles).filter(Role.name.in_(['admin', 'gerente'])).all()
    
    user_data = {
        'id': user.id, 'name': user.name, 'email': user.email,
        'gerente_id': user.gerente_id, 'roles': [role.id for role in user.roles]
    }
    
    return jsonify({
        'success': True, 'user': user_data,
        'all_roles': [{'id': r.id, 'name': r.name} for r in roles],
        'all_managers': [{'id': m.id, 'name': m.name} for m in potential_managers]
    })

@admin.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)
    gerente_id = data.get('gerente_id')
    user.gerente_id = int(gerente_id) if gerente_id else None
    role_ids = data.get('roles', [])
    user.roles = Role.query.filter(Role.id.in_(role_ids)).all()
    db.session.commit()
    return jsonify({'success': True, 'message': 'Usuário atualizado com sucesso!'})

@admin.route('/api/users/<int:user_id>/toggle-status', methods=['POST'])
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        return jsonify({'success': False, 'error': 'Você não pode desativar a si mesmo.'}), 403
    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({'success': True, 'message': f'Status do usuário {user.name} alterado.'})

# --- Rotas para Configurações do Sistema ---
@admin.route('/settings')
def settings():
    """Página de configurações gerais do sistema."""
    return render_template('admin/settings.html')

@admin.route('/api/settings', methods=['GET'])
def get_settings():
    """Busca todas as configurações do banco."""
    settings = ConfigGlobal.query.all()
    settings_dict = {s.key: (decrypt_data(s.value) if s.is_encrypted else s.value) for s in settings}
    return jsonify({'success': True, 'settings': settings_dict})

@admin.route('/api/settings', methods=['POST'])
def save_settings():
    """Salva um conjunto de configurações no banco."""
    data = request.get_json()
    for key, value in data.items():
        setting = ConfigGlobal.query.get(key)
        if not setting:
            setting = ConfigGlobal(key=key)
            db.session.add(setting)
        
        # Criptografa a senha do SMTP antes de salvar
        if key == 'SMTP_PASSWORD':
            setting.value = encrypt_data(value)
            setting.is_encrypted = True
        else:
            setting.value = value
            setting.is_encrypted = False
            
    db.session.commit()
    return jsonify({'success': True, 'message': 'Configurações salvas com sucesso!'})

@admin.route('/api/settings/test-smtp', methods=['POST'])
def test_smtp_settings():
    """Envia um e-mail de teste com as configurações fornecidas."""
    data = request.get_json()
    try:
        # --- Função recebe o dicionário de dados e o destinatário ---
        send_test_email(
            smtp_settings=data,
            test_recipient=current_user.email
        )
        return jsonify({'success': True, 'message': f'E-mail de teste enviado com sucesso para {current_user.email}!'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Falha ao enviar e-mail: {str(e)}'}), 500

# --- Rotas para Gestão de Domínios ---
@admin.route('/domains')
def domain_management():
    """Página de gestão de domínios permitidos."""
    return render_template('admin/domains.html')

@admin.route('/api/domains', methods=['GET'])
def get_domains():
    """Busca todos os domínios permitidos."""
    domains = DominiosPermitidos.query.order_by(DominiosPermitidos.domain).all()
    return jsonify({'success': True, 'domains': [d.to_dict() for d in domains]})

@admin.route('/api/domains', methods=['POST'])
def add_domain():
    """Adiciona um novo domínio permitido."""
    data = request.get_json()
    domain_name = data.get('domain', '').strip().lower()
    if not domain_name:
        return jsonify({'success': False, 'error': 'O nome do domínio é obrigatório.'}), 400
    
    existing = DominiosPermitidos.query.filter_by(domain=domain_name).first()
    if existing:
        return jsonify({'success': False, 'error': 'Este domínio já está cadastrado.'}), 409
        
    new_domain = DominiosPermitidos(domain=domain_name)
    db.session.add(new_domain)
    db.session.commit()
    return jsonify({'success': True, 'domain': new_domain.to_dict()})

@admin.route('/api/domains/<int:domain_id>', methods=['DELETE'])
def delete_domain(domain_id):
    """Remove um domínio permitido."""
    domain = DominiosPermitidos.query.get_or_404(domain_id)
    db.session.delete(domain)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Domínio removido com sucesso.'})

# --- Rota de API para convidar usuários ---
@admin.route('/api/users/invite', methods=['POST'])
def invite_user():
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    name = data.get('name', '').strip()
    role_ids = data.get('roles', [])

    if not email or not name or not role_ids:
        return jsonify({'success': False, 'error': 'Nome, e-mail e pelo menos um papel são obrigatórios.'}), 400

    # 1. Valida se o domínio do e-mail é permitido
    permitidos = DominiosPermitidos.query.all()
    if permitidos: # Se a lista não estiver vazia, a validação é obrigatória
        domain = email.split('@')[-1]
        if not any(d.domain == domain for d in permitidos):
            return jsonify({'success': False, 'error': f'O domínio "{domain}" não está autorizado para receber convites.'}), 403

    # 2. Valida se o e-mail já existe
    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'error': 'Este e-mail já está cadastrado no sistema.'}), 409

    # 3. Cria o novo usuário (inativo) e gera o token
    novo_usuario = User(email=email, name=name)
    novo_usuario.generate_invitation_token()
    
    roles = Role.query.filter(Role.id.in_(role_ids)).all()
    novo_usuario.roles = roles
    
    db.session.add(novo_usuario)
    db.session.commit()

    # 4. Envia o e-mail de convite
    try:
        site_url = ConfigGlobal.get_setting('SITE_URL', request.url_root)
        invitation_link = url_for('auth.set_password_with_token', token=novo_usuario.invitation_token, _external=True)
        # Garante que a URL externa use a URL base configurada
        if 'localhost' in invitation_link or '127.0.0.1' in invitation_link:
             base_url = site_url.strip('/')
             path = url_for('auth.set_password_with_token', token=novo_usuario.invitation_token)
             invitation_link = f"{base_url}{path}"

        send_invitation_email(novo_usuario, invitation_link)
    except Exception as e:
        # Se o e-mail falhar, reverte a criação do usuário para não deixar lixo no banco
        db.session.delete(novo_usuario)
        db.session.commit()
        return jsonify({'success': False, 'error': f'Não foi possível enviar o e-mail de convite. Verifique as configurações de SMTP. Erro: {str(e)}'}), 500

    return jsonify({'success': True, 'message': f'Convite enviado com sucesso para {email}!'})

# --- ADIÇÃO v8.0: Novas rotas para Importação de Dados ---
@admin.route('/import')
def import_data():
    """Página para importação de dados via CSV."""
    return render_template('admin/import.html')

@admin.route('/api/import/template')
def download_template():
    """Fornece o template CSV para download."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Nome Fantasia Empresa', 'CNPJ Empresa', 'Telefone Contato', 'Email Contato', 'Nome Contato', 'Título Oportunidade', 'Valor Oportunidade'])
    # Exemplo completo
    writer.writerow(['Exemplo Fantasia', '00.000.000/0001-00', '(11) 99999-8888', 'contato@exemplo.com', 'João Silva', 'Novo Projeto de TI', '15000.00'])
    # --- ADIÇÃO: Exemplo com dados mínimos ---
    writer.writerow(['Outra Empresa Exemplo', '', '(81) 98877-6655', '', '', '', ''])
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=template_importacao.csv"}
    )

def processar_csv(stream):
    """Função auxiliar para ler e validar o CSV, retornando os dados e um relatório."""
    csv_reader = csv.DictReader(stream)
    report = {'success_count': 0, 'error_count': 0, 'errors': []}
    valid_rows = []
    
    for row_num, row in enumerate(csv_reader, 2):
        nome_fantasia = row.get('Nome Fantasia Empresa', '').strip()
        telefone_contato = row.get('Telefone Contato', '').strip()
        cnpj = row.get('CNPJ Empresa', '').strip()

        if not nome_fantasia or not telefone_contato:
            report['error_count'] += 1
            report['errors'].append(f"Linha {row_num}: 'Nome Fantasia Empresa' e 'Telefone Contato' são obrigatórios.")
            continue

        # --- ALTERAÇÃO: Lógica de validação de duplicatas aprimorada ---
        existing_conta = None
        if cnpj and is_valid_cnpj(cnpj):
            cnpj_hash = get_cnpj_hash(cnpj)
            existing_conta = Conta.query.filter_by(cnpj_hash=cnpj_hash).first()
            if existing_conta:
                report['error_count'] += 1
                report['errors'].append(f"Linha {row_num}: CNPJ '{cnpj}' já pertence à conta '{existing_conta.nome_fantasia}'.")
                continue
        else:
            # Se não há CNPJ, valida pelo nome fantasia normalizado
            normalized_name_search = normalize_name(nome_fantasia)
            # Precisamos buscar em todas as contas e normalizar os nomes para comparar
            all_contas = Conta.query.all()
            for conta in all_contas:
                if normalize_name(conta.nome_fantasia) == normalized_name_search:
                    existing_conta = conta
                    break
            
            if existing_conta:
                report['error_count'] += 1
                report['errors'].append(f"Linha {row_num}: Nome Fantasia '{nome_fantasia}' já pertence à conta '{existing_conta.nome_fantasia}'.")
                continue
            
        valid_rows.append(row)
        report['success_count'] += 1
        
    return valid_rows, report

@admin.route('/api/import/preview', methods=['POST'])
def import_csv_preview():
    """Processa o CSV para validação e retorna um preview."""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'Nenhum arquivo enviado.'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Nenhum arquivo selecionado.'}), 400

    try:
        # Tenta decodificar com UTF-8, se falhar, tenta com ISO-8859-1 (Latin-1)
        try:
            stream = io.StringIO(file.stream.read().decode("UTF-8"), newline=None)
        except UnicodeDecodeError:
            file.stream.seek(0)
            stream = io.StringIO(file.stream.read().decode("ISO-8859-1"), newline=None)

        valid_rows, report = processar_csv(stream)
        
        # Pega os cabeçalhos do CSV original para o preview
        stream.seek(0)
        headers = next(csv.reader(stream))

        return jsonify({
            'success': True,
            'report': report,
            'preview_data': valid_rows,
            'headers': headers
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'Erro ao processar o arquivo: {str(e)}'}), 500

@admin.route('/api/import/execute', methods=['POST'])
def import_csv_execute():
    """Executa a importação com base nos dados validados do preview."""
    data = request.get_json().get('data', [])
    filename = request.get_json().get('filename', 'import.csv')
    
    if not data:
        return jsonify({'success': False, 'error': 'Nenhum dado válido para importar.'}), 400
        
    try:
        success_count = 0
        for row in data:
            nova_conta = Conta(
                user_id=None,
                nome_fantasia=row.get('Nome Fantasia Empresa'),
                razao_social=row.get('Razão Social Empresa', row.get('Nome Fantasia Empresa')),
                cnpj=row.get('CNPJ Empresa') if is_valid_cnpj(row.get('CNPJ Empresa')) else None
            )
            db.session.add(nova_conta)
            db.session.flush()

            novo_contato = Contato(
                conta_id=nova_conta.id,
                nome=row.get('Nome Contato', 'Contato Principal').strip() or 'Contato Principal',
                email=row.get('Email Contato'),
                telefone=row.get('Telefone Contato')
            )
            db.session.add(novo_contato)
            db.session.flush()

            novo_lead = Lead(
                conta_id=nova_conta.id,
                contato_id=novo_contato.id,
                user_id=None,
                titulo=row.get('Título Oportunidade', 'Oportunidade de Prospecção Inicial').strip() or 'Oportunidade de Prospecção Inicial',
                valor_estimado=float(row['Valor Oportunidade']) if row.get('Valor Oportunidade') else None
            )
            db.session.add(novo_lead)
            success_count += 1

        # Cria o registro de histórico
        historico = HistoricoImportacao(
            user_id=current_user.id,
            nome_arquivo=filename,
            sucesso_count=success_count,
            erro_count=0 # Erros já foram filtrados no preview
        )
        db.session.add(historico)
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'{success_count} registros importados com sucesso!'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Ocorreu um erro inesperado durante a importação: {str(e)}'}), 500

# --- ADIÇÃO v8.1: Novas rotas para Histórico de Importações ---
@admin.route('/imports')
def import_history():
    """Página para visualizar o histórico de importações."""
    return render_template('admin/import_history.html')

@admin.route('/api/imports', methods=['GET'])
def get_import_history():
    """API que busca o histórico de importações."""
    history = HistoricoImportacao.query.order_by(HistoricoImportacao.data_importacao.desc()).all()
    return jsonify({'success': True, 'history': [h.to_dict() for h in history]})

@admin.route('/api/import/csv', methods=['POST'])
def import_csv():
    """Processa o upload do arquivo CSV para criar Contas, Contatos e Leads."""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'Nenhum arquivo enviado.'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Nenhum arquivo selecionado.'}), 400

    try:
        stream = io.StringIO(file.stream.read().decode("UTF-8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        report = {'success_count': 0, 'error_count': 0, 'errors': []}
        
        for row_num, row in enumerate(csv_reader, 2):
            nome_fantasia = row.get('Nome Fantasia Empresa', '').strip()
            telefone_contato = row.get('Telefone Contato', '').strip()
            cnpj = row.get('CNPJ Empresa', '').strip()

            if not nome_fantasia or not telefone_contato:
                report['error_count'] += 1
                report['errors'].append(f"Linha {row_num}: 'Nome Fantasia Empresa' e 'Telefone Contato' são obrigatórios.")
                continue

            # --- ALTERAÇÃO: Lógica de validação de duplicatas aprimorada ---
            existing_conta = None
            if cnpj and is_valid_cnpj(cnpj):
                cnpj_hash = get_cnpj_hash(cnpj)
                existing_conta = Conta.query.filter_by(cnpj_hash=cnpj_hash).first()
                if existing_conta:
                    report['error_count'] += 1
                    report['errors'].append(f"Linha {row_num}: CNPJ '{cnpj}' já pertence à conta '{existing_conta.nome_fantasia}'.")
                    continue
            else:
                # Se não há CNPJ, valida pelo nome fantasia normalizado
                normalized_name_search = normalize_name(nome_fantasia)
                # Precisamos buscar em todas as contas e normalizar os nomes para comparar
                all_contas = Conta.query.all()
                for conta in all_contas:
                    if normalize_name(conta.nome_fantasia) == normalized_name_search:
                        existing_conta = conta
                        break
                
                if existing_conta:
                    report['error_count'] += 1
                    report['errors'].append(f"Linha {row_num}: Nome Fantasia '{nome_fantasia}' já pertence à conta '{existing_conta.nome_fantasia}'.")
                    continue
            
            # Se passou por todas as validações, cria as entidades
            nova_conta = Conta(
                user_id=None,
                nome_fantasia=nome_fantasia,
                razao_social=row.get('Razão Social Empresa', nome_fantasia),
                cnpj=cnpj if is_valid_cnpj(cnpj) else None
            )
            db.session.add(nova_conta)
            db.session.flush()

            novo_contato = Contato(
                conta_id=nova_conta.id,
                nome=row.get('Nome Contato', 'Contato Principal').strip() or 'Contato Principal',
                email=row.get('Email Contato', '').strip(),
                telefone=row.get('Telefone Contato', '').strip()
            )
            db.session.add(novo_contato)
            db.session.flush()

            novo_lead = Lead(
                conta_id=nova_conta.id,
                contato_id=novo_contato.id,
                user_id=None,
                titulo=row.get('Título Oportunidade', 'Oportunidade de Prospecção Inicial').strip() or 'Oportunidade de Prospecção Inicial',
                valor_estimado=float(row['Valor Oportunidade']) if row.get('Valor Oportunidade') else None,
                estagio_ciclo_vida='Lead',
                status_lead='Novo',
                temperatura='Morno'
            )
            db.session.add(novo_lead)
            report['success_count'] += 1

        db.session.commit()
        return jsonify({'success': True, 'report': report})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Ocorreu um erro inesperado: {str(e)}'}), 500
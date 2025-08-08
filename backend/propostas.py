from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, Response
from flask_login import login_required, current_user
from .models import Proposta, ItemProposta, ProdutoServico, db, CustoProposta, Conta, Lead, Contato, ConfigGlobal, User, Contato
from .contas import check_permission
from decimal import Decimal
from datetime import datetime
import weasyprint

propostas = Blueprint('propostas', __name__)

# --- ROTAS DE PÁGINA ---
# --- Rota para a página de listagem ---
@propostas.route('/propostas')
@login_required
def listar_propostas():
    """Renderiza a página de listagem de propostas."""
    return render_template('propostas/lista_propostas.html')

@propostas.route('/propostas/<int:proposta_id>')
@login_required
def detalhe_proposta(proposta_id):
    proposta = Proposta.query.get_or_404(proposta_id)
    # A permissão para ver a proposta deriva da permissão para ver a conta
    if not check_permission(proposta.lead.conta, for_editing=False):
        flash("Você não tem permissão para ver esta proposta.", "danger")
        return redirect(url_for('contas.listar_contas'))
        
    return render_template('propostas/detalhe_proposta.html', proposta=proposta)

# --- ADIÇÃO v12.0: Rota para gerar o PDF da proposta ---
@propostas.route('/propostas/<int:proposta_id>/pdf')
@login_required
def gerar_proposta_pdf(proposta_id):
    proposta = Proposta.query.get_or_404(proposta_id)
    if not check_permission(proposta.lead.conta):
        abort(403)

    # Coleta todas as informações necessárias para o template
    dados_empresa = {key: ConfigGlobal.get_setting(key, '') for key in ['COMPANY_NAME', 'COMPANY_CONTACT', 'COMPANY_ADDRESS']}
    textos_proposta = {key: ConfigGlobal.get_setting(key, '') for key in ['PROPOSAL_GREETING', 'PROPOSAL_COMMERCIAL', 'PROPOSAL_CONFIDENTIALITY']}
    
    html = render_template(
        'propostas/proposta_pdf_template.html', 
        proposta=proposta,
        empresa=dados_empresa,
        textos=textos_proposta
    )
    
    pdf = weasyprint.HTML(string=html).write_pdf()
    
    return Response(pdf, mimetype='application/pdf', headers={
        'Content-Disposition': f'attachment; filename="proposta_{proposta.numero_proposta}.pdf"'
    })

# --- ROTAS DE API ---
# --- API para buscar e paginar propostas ---
@propostas.route('/api/propostas', methods=['GET'])
@login_required
def get_propostas():
    page = request.args.get('page', 1, type=int)
    per_page = 15

    # --- CORREÇÃO: Especifica a condição do join para remover a ambiguidade ---
    query = Proposta.query.join(Lead, Proposta.lead_id == Lead.id).join(Conta)

    if current_user.has_role('gerente'):
        liderados_ids = [liderado.id for liderado in current_user.liderados]
        liderados_ids.append(current_user.id)
        query = query.filter(Conta.user_id.in_(liderados_ids))
    elif not current_user.has_role('admin'):
        query = query.filter(Conta.user_id == current_user.id)

    pagination = query.order_by(Proposta.data_criacao.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    propostas_list = []
    for prop in pagination.items:
        prop_dict = prop.to_dict()
        prop_dict['conta_nome'] = prop.lead.conta.nome_fantasia
        prop_dict['lead_titulo'] = prop.lead.titulo
        prop_dict['criador_nome'] = prop.criador.name
        propostas_list.append(prop_dict)

    return jsonify({
        'success': True,
        'propostas': propostas_list,
        'pagination': {
            'total': pagination.total, 'pages': pagination.pages, 'has_prev': pagination.has_prev,
            'has_next': pagination.has_next, 'page': pagination.page
        }
    })

# --- ADIÇÃO: API de detalhes da proposta com contatos da conta ---
@propostas.route('/api/propostas/<int:proposta_id>/details', methods=['GET'])
@login_required
def get_proposta_details(proposta_id):
    proposta = Proposta.query.get_or_404(proposta_id)
    if not check_permission(proposta.lead.conta, for_editing=False):
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403

    itens_catalogo = ProdutoServico.query.filter_by(is_active=True).order_by(ProdutoServico.nome).all()
    # --- CORREÇÃO: Busca os contatos da conta para popular o dropdown ---
    contatos_conta = Contato.query.filter_by(conta_id=proposta.lead.conta_id, is_active=True).all()

    return jsonify({
        'success': True,
        'proposta': proposta.to_dict(),
        'itens': [item.to_dict() for item in proposta.itens.order_by(ItemProposta.id).all()],
        'custos': [custo.to_dict() for custo in proposta.custos.order_by(CustoProposta.id).all()],
        'catalogo': [item.to_dict() for item in itens_catalogo],
        'contatos': [c.to_dict() for c in contatos_conta]
    })

# --- API de detalhes agora inclui os custos ---
# --- ALTERAÇÃO v12.0: API centralizada para salvar todos os dados de gestão ---
@propostas.route('/api/propostas/<int:proposta_id>/management', methods=['PUT'])
@login_required
def update_proposta_management(proposta_id):
    proposta = Proposta.query.get_or_404(proposta_id)
    if not check_permission(proposta.lead.conta, for_editing=True):
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
        
    data = request.get_json()
    
    proposta.status = data.get('status', proposta.status)
    
    # Lógica corrigida para salvar o contato_id
    contato_id_str = data.get('contato_id')
    if contato_id_str and str(contato_id_str).isdigit():
        proposta.contato_id = int(contato_id_str)
    else:
        proposta.contato_id = None

    try:
        if data.get('data_envio'):
            proposta.data_envio = datetime.strptime(data['data_envio'], '%Y-%m-%d')
        else:
            proposta.data_envio = None
            
        if data.get('data_validade'):
            proposta.data_validade = datetime.strptime(data['data_validade'], '%Y-%m-%d')
        else:
            proposta.data_validade = None
    except (ValueError, TypeError):
        pass

    db.session.commit()
    return jsonify({'success': True, 'proposta': proposta.to_dict()})

@propostas.route('/api/propostas/<int:proposta_id>/items', methods=['POST'])
@login_required
def add_item_proposta(proposta_id):
    proposta = Proposta.query.get_or_404(proposta_id)
    if not check_permission(proposta.lead.conta, for_editing=True):
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403

    data = request.get_json()
    
    # --- Converte os valores para Decimal antes de usar ---
    try:
        quantidade = Decimal(data['quantidade'])
        valor_unitario = Decimal(data['valor_unitario'])
    except (TypeError, ValueError):
        return jsonify({'success': False, 'error': 'Quantidade e Valor Unitário devem ser números válidos.'}), 400

    novo_item = ItemProposta(
        proposta_id=proposta.id,
        produto_servico_id=data.get('produto_servico_id') or None,
        descricao=data['descricao'],
        quantidade=quantidade,
        valor_unitario=valor_unitario
    )
    novo_item.valor_total = novo_item.quantidade * novo_item.valor_unitario
    
    db.session.add(novo_item)
    
    # Atualiza o valor total da proposta
    proposta.valor_total = Decimal(proposta.valor_total) + novo_item.valor_total
    
    db.session.commit()
    
    return jsonify({'success': True, 'item': novo_item.to_dict()})

# --- API para excluir um item da proposta ---
@propostas.route('/api/propostas/items/<int:item_id>', methods=['DELETE'])
@login_required
def delete_item_proposta(item_id):
    item = ItemProposta.query.get_or_404(item_id)
    proposta = item.proposta
    
    if not check_permission(proposta.lead.conta, for_editing=True):
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
        
    try:
        # Subtrai o valor do item do total da proposta
        proposta.valor_total = Decimal(proposta.valor_total) - item.valor_total
        
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Item removido com sucesso.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Ocorreu um erro: {str(e)}'}), 500

# --- APIs para gerenciar custos ---
@propostas.route('/api/propostas/<int:proposta_id>/custos', methods=['POST'])
@login_required
def add_custo_proposta(proposta_id):
    proposta = Proposta.query.get_or_404(proposta_id)
    if not check_permission(proposta.lead.conta, for_editing=True):
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403

    data = request.get_json()
    try:
        novo_custo = CustoProposta(
            proposta_id=proposta.id,
            descricao=data['descricao'],
            tipo_custo=data['tipo_custo'],
            valor=Decimal(data['valor'])
        )
        db.session.add(novo_custo)
        db.session.commit()
        return jsonify({'success': True, 'custo': novo_custo.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Erro ao adicionar custo: {str(e)}'}), 500

@propostas.route('/api/propostas/custos/<int:custo_id>', methods=['DELETE'])
@login_required
def delete_custo_proposta(custo_id):
    custo = CustoProposta.query.get_or_404(custo_id)
    proposta = custo.proposta
    if not check_permission(proposta.lead.conta, for_editing=True):
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
        
    try:
        db.session.delete(custo)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Custo removido com sucesso.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Ocorreu um erro: {str(e)}'}), 500

# --- APIs para o Ciclo de Vida da Proposta ---
@propostas.route('/api/propostas/<int:proposta_id>/status', methods=['PUT'])
@login_required
def update_proposta_status(proposta_id):
    proposta = Proposta.query.get_or_404(proposta_id)
    if not check_permission(proposta.lead.conta, for_editing=True):
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403
        
    data = request.get_json()
    proposta.status = data.get('status', proposta.status)
    
    if data.get('data_envio'):
        proposta.data_envio = datetime.strptime(data['data_envio'], '%Y-%m-%d')
    if data.get('data_validade'):
        proposta.data_validade = datetime.strptime(data['data_validade'], '%Y-%m-%d')

    db.session.commit()
    return jsonify({'success': True, 'proposta': proposta.to_dict()})

@propostas.route('/api/propostas/<int:proposta_id>/duplicate', methods=['POST'])
@login_required
def duplicate_proposta(proposta_id):
    proposta_original = Proposta.query.get_or_404(proposta_id)
    if not check_permission(proposta_original.lead.conta, for_editing=True):
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403

    # Lógica de versionamento
    versao_major = int(proposta_original.versao.split('.')[0])
    nova_versao = f"{versao_major + 1}.0"

    nova_proposta = Proposta(
        lead_id=proposta_original.lead_id,
        user_id=current_user.id,
        contato_id=proposta_original.contato_id,
        numero_proposta=f"{proposta_original.numero_proposta.split('-V')[0]}-V{versao_major + 1}",
        versao=nova_versao,
        status='Em elaboração',
        valor_total=proposta_original.valor_total
    )
    db.session.add(nova_proposta)

    # Copia os itens
    for item in proposta_original.itens:
        novo_item = ItemProposta(proposta=nova_proposta, **item.to_dict(exclude_id=True))
        db.session.add(novo_item)
        
    # Copia os custos
    for custo in proposta_original.custos:
        novo_custo = CustoProposta(proposta=nova_proposta, **custo.to_dict(exclude_id=True))
        db.session.add(novo_custo)

    db.session.commit()
    
    redirect_url = url_for('propostas.detalhe_proposta', proposta_id=nova_proposta.id)
    return jsonify({'success': True, 'redirect_url': redirect_url})

# --- ADIÇÃO v12.0: Nova API para salvar dados gerais da proposta ---
@propostas.route('/api/propostas/<int:proposta_id>/general', methods=['PUT'])
@login_required
def update_proposta_general(proposta_id):
    proposta = Proposta.query.get_or_404(proposta_id)
    if not check_permission(proposta.lead.conta, for_editing=True):
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403

    data = request.get_json()
    
    if data.get('contato_id'):
        proposta.contato_id = data.get('contato_id')
    
    if data.get('data_envio'):
        proposta.data_envio = datetime.strptime(data['data_envio'], '%Y-%m-%d')
    else:
        proposta.data_envio = None
        
    if data.get('data_validade'):
        proposta.data_validade = datetime.strptime(data['data_validade'], '%Y-%m-%d')
    else:
        proposta.data_validade = None
        
    db.session.commit()
    return jsonify({'success': True, 'message': 'Dados da proposta atualizados.'})
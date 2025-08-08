from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
# --- ALTERAÇÃO v11.1: Importa o novo modelo de Custo ---
from .models import Proposta, ItemProposta, ProdutoServico, db, CustoProposta
from .contas import check_permission
from decimal import Decimal

propostas = Blueprint('propostas', __name__)

# --- ROTAS DE PÁGINA ---
@propostas.route('/propostas/<int:proposta_id>')
@login_required
def detalhe_proposta(proposta_id):
    proposta = Proposta.query.get_or_404(proposta_id)
    # A permissão para ver a proposta deriva da permissão para ver a conta
    if not check_permission(proposta.lead.conta, for_editing=False):
        flash("Você não tem permissão para ver esta proposta.", "danger")
        return redirect(url_for('contas.listar_contas'))
        
    return render_template('propostas/detalhe_proposta.html', proposta=proposta)

# --- ROTAS DE API ---
# --- ALTERAÇÃO v11.1: API de detalhes agora inclui os custos ---
@propostas.route('/api/propostas/<int:proposta_id>/details', methods=['GET'])
@login_required
def get_proposta_details(proposta_id):
    proposta = Proposta.query.get_or_404(proposta_id)
    if not check_permission(proposta.lead.conta, for_editing=False):
        return jsonify({'success': False, 'error': 'Acesso negado'}), 403

    itens_catalogo = ProdutoServico.query.filter_by(is_active=True).order_by(ProdutoServico.nome).all()

    return jsonify({
        'success': True,
        'proposta': proposta.to_dict(),
        'itens': [item.to_dict() for item in proposta.itens.order_by(ItemProposta.id).all()],
        'custos': [custo.to_dict() for custo in proposta.custos.order_by(CustoProposta.id).all()],
        'catalogo': [item.to_dict() for item in itens_catalogo]
    })

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
    proposta.valor_total = proposta.valor_total + novo_item.valor_total
    
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

# --- ADIÇÃO v11.1: Novas APIs para gerenciar custos ---
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
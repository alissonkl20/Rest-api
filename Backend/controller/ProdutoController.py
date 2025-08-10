from flask import Blueprint, request, jsonify, abort
from http import HTTPStatus
from decimal import Decimal
from model.ProdutoModel import ProdutoModel
from repository.ProdutoRepository import ProdutoRepository

produto_bp = Blueprint('produtos', __name__, url_prefix='/api/produtos')
repo = ProdutoRepository()

# Novo endpoint GET para listar todos os produtos
@produto_bp.route('/', methods=['GET'])
def listar_produtos():
    produtos = repo.find_all()
    return jsonify([produto.to_dict() for produto in produtos])

@produto_bp.route('/', methods=['POST'])
def criar_produto():
    data = request.get_json()
    
    required_fields = ['nome', 'preco', 'categoria_id']
    if not all(field in data for field in required_fields):
        abort(HTTPStatus.BAD_REQUEST, description="Campos obrigatórios faltando")
    
    try:
        produto = ProdutoModel(
            nome=data['nome'],
            preco=Decimal(str(data['preco'])),
            disponivel=data.get('disponivel', True),
            categoria_id=data['categoria_id']
        )
        repo.save(produto)
        return jsonify(produto.to_dict()), HTTPStatus.CREATED  # Adicionado status code
    except ValueError as e:
        abort(HTTPStatus.BAD_REQUEST, description=str(e))

# ... (outros endpoints permanecem iguais) ...
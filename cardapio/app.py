from flask import Flask, render_template
from datetime import datetime
import requests
from flask_cors import CORS
import time

app = Flask(__name__,
            static_folder='static',
            template_folder='templates')
CORS(app)

API_BASE_URL = 'http://127.0.0.1:5000/api'

def get_api_data(endpoint):
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar {endpoint}: {str(e)}")
        return None

def normalizar_nome_categoria(nome):
    # Remove espaços extras e padroniza os nomes
    nome = nome.strip()
    substituicoes = {
        'Paes': 'Pães',
        'Mousses': 'Mousses',
        'Bolos': 'Bolos',
        'Salgados': 'Pastéis'  # Mapeando Salgados para Pastéis
    }
    return substituicoes.get(nome, nome)

def agrupar_por_categoria(produtos):
    if produtos is None:
        return {"categorias": {}, "total_produtos": 0}
    
    categorias = {
        "Pães": {"disponiveis": [], "indisponiveis": []},
        "Bolos": {"disponiveis": [], "indisponiveis": []},
        "Mousses": {"disponiveis": [], "indisponiveis": []},
        "Pastéis": {"disponiveis": [], "indisponiveis": []}
    }
    
    for produto in produtos:
        try:
            nome_categoria = normalizar_nome_categoria(produto.get("categoria_nome", "Sem categoria"))
            if nome_categoria not in categorias:
                continue
                
            produto_formatado = {
                "nome": produto.get("nome", "Sem nome"),
                "preco": float(produto.get("preco", 0))
            }
            
            if produto.get("disponivel", False):
                categorias[nome_categoria]["disponiveis"].append(produto_formatado)
            else:
                categorias[nome_categoria]["indisponiveis"].append(produto_formatado)
        except Exception as e:
            print(f"Erro ao processar produto: {e}")
            continue
    
    return {
        "categorias": categorias,
        "total_produtos": len(produtos) if produtos else 0
    }

@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/cardapio')
def dashboard():
    try:
        produtos = get_api_data("produtos")
        
        if produtos is None:
            return render_template('cardapio.html', dados={
                'erro': 'Não foi possível obter os produtos do servidor',
                'atualizado_em': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'categorias': {
                    "Pães": {"disponiveis": [], "indisponiveis": []},
                    "Bolos": {"disponiveis": [], "indisponiveis": []},
                    "Mousses": {"disponiveis": [], "indisponiveis": []},
                    "Pastéis": {"disponiveis": [], "indisponiveis": []}
                },
                'total_produtos': 0
            })
        
        dados_agrupados = agrupar_por_categoria(produtos)
        
        return render_template('cardapio.html', dados={
            'categorias': dados_agrupados['categorias'],
            'total_produtos': dados_agrupados['total_produtos'],
            'atualizado_em': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'erro': None
        })
        
    except Exception as e:
        return render_template('cardapio.html', dados={
            'erro': f'Erro no sistema: {str(e)}',
            'atualizado_em': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'categorias': {
                "Pães": {"disponiveis": [], "indisponiveis": []},
                "Bolos": {"disponiveis": [], "indisponiveis": []},
                "Mousses": {"disponiveis": [], "indisponiveis": []},
                "Pastéis": {"disponiveis": [], "indisponiveis": []}
            },
            'total_produtos': 0
        })

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
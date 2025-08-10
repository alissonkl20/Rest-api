from flask import Flask, render_template
from datetime import datetime
import requests
from collections import defaultdict
import time

app = Flask(__name__,
            static_folder='static',
            template_folder='templates')

API_BASE_URL = 'http://127.0.0.1:5000/api' 

def get_api_data(endpoint):
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar {endpoint}: {str(e)}")
        return None

def agrupar_por_categoria(produtos):
    if produtos is None:
        return {"categorias": defaultdict(dict), "total_produtos": 0}
    
    categorias = defaultdict(lambda: {"disponiveis": [], "indisponiveis": []})
    for produto in produtos:
        try:
            # Ajuste para a estrutura esperada
            nome_categoria = produto.get("categoria", {}).get("nome", "Sem categoria")
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
        "categorias": dict(categorias),  # Convertendo para dict padrão
        "total_produtos": len(produtos) if produtos else 0
    }

@app.route('/')
def dashboard():
    try:
        produtos = get_api_data("produtos")
        
        if produtos is None:
            return render_template('cardapio.html', dados={
                'erro': 'Não foi possível obter os produtos do servidor',
                'atualizado_em': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'categorias': {},
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
            'categorias': {},
            'total_produtos': 0
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
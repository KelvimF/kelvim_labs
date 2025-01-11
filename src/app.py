import re
import requests
from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# Configuração do MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['api_db']
clientes = db['clientes']
produtos = db['produtos']

# Função para criar a URL de listagem de produtos
def criar_url_listagem_produtos(pagina=1):
    return f"http://challenge-api.luizalabs.com/api/product/?page={pagina}"

# Função para criar a URL de detalhe de produto
def criar_url_detalhe_produto(produto_id):
    return f"http://challenge-api.luizalabs.com/api/product/{produto_id}/"

# Rota inicial e configuração do flask (GET)
@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Bem-vindo à API Flask! O servidor está rodando."}), 200

# Rota para criar clientes (POST)
@app.route('/clientes', methods=['POST'])
def criar_cliente():
    data = request.json
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    if not nome or not email or not senha:
        return jsonify({"erro": "Nome, email e senha são obrigatórios"}), 400

    # Verifica se o email já está registrado
    if clientes.find_one({"email": email}):
        return jsonify({"erro": "Email já registrado"}), 400

    # Criação do novo cliente
    novo_cliente = {
        "name": nome,
        "email": email,
        "password": senha,  # Senha sem criptografia conforme solicitado
        "favorites": []  # Inicializa a lista de favoritos vazia
    }

    result = clientes.insert_one(novo_cliente)
    cliente_id = str(result.inserted_id)

    return jsonify({"_id": cliente_id}), 201

# Rota para listar clientes (GET)
@app.route('/clientes', methods=['GET'])
def listar_clientes():
    all_clientes = clientes.find()
    clientes_list = []
    for cliente in all_clientes:
        cliente['_id'] = str(cliente['_id'])  # Converte ObjectId para string
        clientes_list.append(cliente)
    return jsonify(clientes_list), 200

# Rota para editar cliente (PUT)
@app.route('/clientes/<id_cliente>', methods=['PUT'])
def editar_cliente(id_cliente):
    data = request.json
    nome = data.get('name')
    email = data.get('email')
    senha = data.get('password')

    if not nome and not email and not senha:
        return jsonify({"erro": "Pelo menos um campo (nome, email ou senha) deve ser informado"}), 400

    # Atualiza os campos fornecidos
    update_fields = {}
    if nome:
        update_fields['name'] = nome
    if email:
        update_fields['email'] = email
    if senha:
        update_fields['password'] = senha

    clientes.update_one({"_id": ObjectId(id_cliente)}, {"$set": update_fields})
    return jsonify({"message": "Cliente atualizado com sucesso"}), 200

# Rota para deletar cliente (DELETE)
@app.route('/clientes/<id_cliente>', methods=['DELETE'])
def deletar_cliente(id_cliente):
    clientes.delete_one({"_id": ObjectId(id_cliente)})
    return jsonify({"message": "Cliente deletado com sucesso"}), 200

# Rota para login (POST)
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    senha = data.get('password')

    if not email or not senha:
        return jsonify({"erro": "Email e senha são obrigatórios"}), 400

    # Verifica se o cliente existe
    cliente = clientes.find_one({"email": email})
    if not cliente:
        return jsonify({"erro": "Cliente não encontrado"}), 404

    # Verifica a senha
    if cliente["password"] != senha:
        return jsonify({"erro": "Senha incorreta"}), 400

    return jsonify({"message": "Login bem-sucedido"}), 200

# Rota para listar os usuários logados (GET)
@app.route('/login', methods=['GET'])
def get_cliente():
    email = request.args.get('email')  # Email será passado como parâmetro na URL

    if not email:
        # Retorna todos os IDs e emails logados
        all_clientes = clientes.find({}, {"_id": 1, "email": 1})
        clientes_list = [
            {"_id": str(cliente["_id"]), "email": cliente.get("email", "Email não informado")}
            for cliente in all_clientes
        ]
        return jsonify({"clientes": clientes_list}), 200

    # Busca um cliente específico pelo email
    cliente = clientes.find_one({"email": email})
    if not cliente:
        return jsonify({"erro": "Cliente não encontrado"}), 404

    # Retorna informações básicas do cliente
    return jsonify({
        "_id": str(cliente["_id"]),  # Converte ObjectId para string
        "name": cliente.get("name", "Nome não informado"),
    }), 200


# Função para buscar produto no banco de dados (simulando a busca na API externa)
def buscar_produto_externo(navigation_id):
    produto = produtos.find_one({"navigation_id": navigation_id})
    if produto:
        # Converte o ObjectId para string e retorna os dados do produto
        produto['_id'] = str(produto['_id'])
        return produto
    return None

# Rota para adicionar produto aos favoritos (POST)
@app.route("/clientes/<id_cliente>/favoritos", methods=["POST"])
def adicionar_favorito(id_cliente):
    try:
        data = request.json
        navigation_id = data.get("navigation_id")

        if not navigation_id:
            return jsonify({"erro": "Navigation ID é obrigatório"}), 400

        # Busca o produto no banco de dados
        product_data = buscar_produto_externo(navigation_id)
        if not product_data:
            return jsonify({"erro": "Produto não encontrado"}), 404

        # Verifica se o cliente existe
        try:
            cliente = clientes.find_one({"_id": ObjectId(id_cliente)})
        except Exception:
            return jsonify({"erro": "ID de cliente inválido"}), 400

        if not cliente:
            return jsonify({"erro": "Cliente não encontrado"}), 404

        # Verifica se o produto já está nos favoritos
        favoritos = cliente.get("favorites", [])
        if any(f["navigation_id"] == navigation_id for f in favoritos):
            return jsonify({"erro": "Produto já está nos favoritos"}), 400

        # Adiciona o produto aos favoritos
        clientes.update_one(
            {"_id": ObjectId(id_cliente)},
            {"$push": {"favorites": {
                "navigation_id": product_data.get('navigation_id'),
                "title": product_data.get('title'),
                "price": product_data.get('price'),
                "image": product_data.get('image'),
                "brand": product_data.get('brand'),
                "review_score": product_data.get('review_score', None)  # Valor padrão
            }}}
        )

        return jsonify({"message": "Produto adicionado aos favoritos com sucesso"}), 201

    except Exception as e:
        print(f"Erro ao adicionar favorito: {e}")
        return jsonify({"erro": "Erro interno no servidor"}), 500

# Rota para listar os favoritos de um cliente (GET)
@app.route("/clientes/<id_cliente>/favoritos", methods=["GET"])
def listar_favoritos(id_cliente):
    cliente = clientes.find_one({"_id": ObjectId(id_cliente)})
    if not cliente:
        return jsonify({"erro": "Cliente não encontrado"}), 404

    # Recupera os produtos favoritos do cliente
    favoritos = cliente.get("favorites", [])
    if not favoritos:
        return jsonify({"message": "Nenhum produto nos favoritos"}), 200

    return jsonify(favoritos), 200

# Rota para remover produto dos favoritos (DELETE)
@app.route("/clientes/<id_cliente>/favoritos/<navigation_id>", methods=["DELETE"])
def remover_favorito(id_cliente, navigation_id):
    cliente = clientes.find_one({"_id": ObjectId(id_cliente)})
    if not cliente:
        return jsonify({"erro": "Cliente não encontrado"}), 404

    # Verifica se o produto está nos favoritos
    if not any(f["navigation_id"] == navigation_id for f in cliente.get("favorites", [])):
        return jsonify({"erro": "Produto não encontrado nos favoritos"}), 404

    # Remove o produto dos favoritos
    clientes.update_one(
        {"_id": ObjectId(id_cliente)},
        {"$pull": {"favorites": {"navigation_id": navigation_id}}}
    )

    return jsonify({"message": "Produto removido dos favoritos com sucesso"}), 200

# Rota para criar produtos (POST)
@app.route('/produtos', methods=['POST'])
def criar_produto():
    data = request.json
    title = data.get('title')
    price = data.get('price')
    description = data.get('description')
    image = data.get('image')
    brand = data.get('brand')
    navigation_id = data.get('navigation_id')

    # Validações dos campos obrigatórios
    if not title or not price or not description or not image or not brand or not navigation_id:
        return jsonify({"erro": "Title, price, description, image, brand e navigation_id são obrigatórios"}), 400

    # Valida o formato do navigation_id (alfanumérico, 10 caracteres)
    if not re.fullmatch(r'^[a-zA-Z0-9]{10}$', navigation_id):
        return jsonify({"erro": "O navigation_id deve ser alfanumérico e conter exatamente 10 caracteres"}), 400

    # Verifica se o navigation_id já existe
    if produtos.find_one({"navigation_id": navigation_id}):
        return jsonify({"erro": "Já existe um produto com este navigation_id"}), 400

    # Criação do novo produto
    novo_produto = {
        "title": title,
        "price": price,
        "description": description,
        "image": image,
        "brand": brand,
        "navigation_id": navigation_id  # Adiciona o navigation_id ao documento
    }

    result = produtos.insert_one(novo_produto)
    produto_id = str(result.inserted_id)

    return jsonify({"_id": produto_id}), 201

# Rota para listar produtos (GET)
@app.route('/produtos', methods=['GET'])
@app.route('/produtos/<id_produto>', methods=['GET'])
def listar_produtos(id_produto=None):
    if id_produto:
        # Caso o ID do produto seja informado na URL, retorna o produto correspondente
        try:
            produto = produtos.find_one({"_id": ObjectId(id_produto)})
        except:
            return jsonify({"erro": "ID do produto inválido"}), 400

        if not produto:
            return jsonify({"erro": "Produto não encontrado"}), 404

        produto['_id'] = str(produto['_id'])  # Converte ObjectId para string
        return jsonify(produto), 200

    # Busca por navigation_id via query string
    navigation_id = request.args.get('navigation_id')
    if navigation_id:
        produto = produtos.find_one({"navigation_id": navigation_id})
        if not produto:
            return jsonify({"erro": "Produto com o navigation_id informado não encontrado"}), 404

        produto['_id'] = str(produto['_id'])  # Converte ObjectId para string
        return jsonify(produto), 200

    # Caso contrário, retorna todos os produtos
    all_produtos = produtos.find()
    produtos_list = []
    for produto in all_produtos:
        produto['_id'] = str(produto['_id'])
        produtos_list.append(produto)

    return jsonify(produtos_list), 200

# Rota para editar produto (PUT)
@app.route('/produtos/<id_produto>', methods=['PUT'])
def editar_produto(id_produto):
    data = request.json
    title = data.get('title')
    price = data.get('price')
    description = data.get('description')
    image = data.get('image')
    brand = data.get('brand')

    if not title and not price and not description and not image and not brand:
        return jsonify({"erro": "Pelo menos um campo (title, price, description, image ou brand) deve ser informado"}), 400

    # Atualiza os campos fornecidos
    update_fields = {}
    if title:
        update_fields['title'] = title
    if price:
        update_fields['price'] = price
    if description:
        update_fields['description'] = description
    if image:
        update_fields['image'] = image
    if brand:
        update_fields['brand'] = brand

    produtos.update_one({"_id": ObjectId(id_produto)}, {"$set": update_fields})
    return jsonify({"message": "Produto atualizado com sucesso"}), 200

# Rota para deletar produto (DELETE)
@app.route('/produtos/<id_produto>', methods=['DELETE'])
def deletar_produto(id_produto):
    produtos.delete_one({"_id": ObjectId(id_produto)})
    return jsonify({"message": "Produto deletado com sucesso"}), 200

# Rodando a aplicação Flask
if __name__ == '__main__':
    app.run(debug=True)

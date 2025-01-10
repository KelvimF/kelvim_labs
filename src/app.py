from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# Configuração inicial do MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['api_db'] 
clientes = db['clientes']
produtos = db['produtos']



# Rota inicial de configuração do Flask
@app.route('/')
def home():
    return "Flask configurado com sucesso!"



# Rota de conexão com o MongoDB
@app.route('/test-db')
def test_db():
    try:
        db.command("ping")
        return "Conexão com o MongoDB estabelecida com sucesso!"
    except Exception as e:
        return f"Erro ao conectar ao MongoDB: {e}"



# Rota para criar clientes
@app.route("/clientes", methods=["POST"])
def criar_clientes():
    data = request.json
    
    # Verifica se os campos obrigatórios estão presentes
    if not data.get("nome") or not data.get("email"):
        return jsonify({"erro": "Nome e email são obrigatórios. Preencha todos os campos para continuar o cadastro"}), 400
    
    # Verifica se o e-mail já está cadastrado
    if clientes.find_one({"email": data["email"]}):
        return jsonify({"erro": "Email já está em uso."}), 400

    # Criação de novos clientes
    novo_cliente = {
        "nome": data["nome"],
        "email": data["email"],
        "telefone": data.get("telefone")
    }
    result = clientes.insert_one(novo_cliente)

    # Retorna o ID do cliente que foi criado
    return jsonify({"_id": str(result.inserted_id)}), 201



# Rota para listar os clientes cadastrados na API
@app.route("/clientes", methods=["GET"])
def list_customers():
    try:
        print("Recebendo requisição para listar clientes...")
        listar_clientes = [
            {**cliente, "_id": str(cliente["_id"])}
            for cliente in clientes.find()
        ]
        print(f"{len(listar_clientes)} clientes encontrados.")
        return jsonify(listar_clientes), 200
    except Exception as e:
        print(f"Erro ao listar clientes: {e}")
        return jsonify({"erro": f"Erro ao listar clientes: {e}"}), 500



# Atualização de cadastro de clientes
@app.route("/clientes/<id_cliente>", methods=["PUT"])
def update_customer(id_cliente):
    data = request.json
    if not data:
        return jsonify({"erro": "Dados para atualização não fornecidos"}), 400

    update_fields = {key: data[key] for key in data if key in {"nome", "email", "telefone"}}
    if not update_fields:
        return jsonify({"erro": "Nenhum campo válido para atualização"}), 400

    try:
        result = clientes.update_one({"_id": ObjectId(id_cliente)}, {"$set": update_fields})
        if result.matched_count == 0:
            return jsonify({"erro": "Cliente não encontrado"}), 404

        return jsonify({"message": "Cliente atualizado com sucesso"}), 200
    except Exception as e:
        return jsonify({"erro": f"Erro ao atualizar cliente: {e}"}), 500



# Exclusão de cadastro de clientes
@app.route("/clientes/<id_cliente>", methods=["DELETE"])
def deletar_clientes(id_cliente):
    try:
        result = clientes.delete_one({"_id": ObjectId(id_cliente)})
        if result.deleted_count == 0:
            return jsonify({"erro": "Cliente não encontrado"}), 404
        return jsonify({"message": "Cliente deletado com sucesso"}), 200
    except Exception as e:
        return jsonify({"erro": f"Erro ao deletar cliente: {e}"}), 500



# Rota para adicionar produtos
@app.route("/produtos", methods=["POST"])
def adicionar_produto():
    data = request.json
    navigation_id = data.get("navigation_id")
    nome = data.get("nome")
    preco = data.get("preco")

    if not navigation_id or not nome or not preco:
        return jsonify({"erro": "navigation_id, nome e preco são obrigatórios"}), 400

    # Verifica se o produto já existe
    produto_existente = produtos.find_one({"navigation_id": navigation_id})
    if produto_existente:
        return jsonify({"erro": "Produto já existe"}), 400

    # Cria um novo produto
    novo_produto = {
        "navigation_id": navigation_id,
        "nome": nome,
        "preco": preco
    }
    result = produtos.insert_one(novo_produto)

    return jsonify({"_id": str(result.inserted_id), "navigation_id": navigation_id}), 201


# Rota para listar produtos
@app.route("/produtos", methods=["GET"])
def listar_produtos():
    # Recupera todos os produtos da coleção 'produtos'
    lista_produtos = list(produtos.find())
    
    if not lista_produtos:
        return jsonify({"message": "Nenhum produto encontrado"}), 200
    
    # Formata a resposta
    produtos_formatados = [
        {**produto, "_id": str(produto["_id"])} for produto in lista_produtos
    ]
    
    return jsonify(produtos_formatados), 200


# Rota para atualizar um produto
@app.route("/produtos/<navigation_id>", methods=["PUT"])
def atualizar_produto(navigation_id):
    data = request.json
    nome = data.get("nome")
    preco = data.get("preco")

    if not nome and not preco:
        return jsonify({"erro": "Nome ou preço precisam ser fornecidos"}), 400

    # Verifica se o produto existe
    produto = produtos.find_one({"navigation_id": navigation_id})
    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404

    # Atualiza o produto
    update_fields = {}
    if nome:
        update_fields["nome"] = nome
    if preco:
        update_fields["preco"] = preco

    produtos.update_one(
        {"navigation_id": navigation_id},
        {"$set": update_fields}
    )

    return jsonify({"message": "Produto atualizado com sucesso"}), 200


# Rota para excluir um produto
@app.route("/produtos/<navigation_id>", methods=["DELETE"])
def excluir_produto(navigation_id):
    # Verifica se o produto existe
    produto = produtos.find_one({"navigation_id": navigation_id})
    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404

    # Remove o produto
    produtos.delete_one({"navigation_id": navigation_id})

    return jsonify({"message": "Produto excluído com sucesso"}), 200



# Rota para favoritos
@app.route("/clientes/<id_cliente>/favoritos", methods=["POST"])
def adicionar_favorito(id_cliente):
    data = request.json
    navigation_id = data.get("navigation_id")
    
    if not navigation_id:
        return jsonify({"erro": "Navigation ID é obrigatório"}), 400

    # Verifica se o produto existe na coleção de produtos
    produto = produtos.find_one({"navigation_id": navigation_id})
    if not produto:
        return jsonify({"erro": "Produto com o navigation ID não encontrado"}), 404

    # Verifica se o cliente existe
    cliente = clientes.find_one({"_id": ObjectId(id_cliente)})
    if not cliente:
        return jsonify({"erro": "Cliente não encontrado"}), 404

    # Verifica se o navigation_id já está nos favoritos
    if "favoritos" in cliente and navigation_id in cliente["favoritos"]:
        return jsonify({"erro": "Produto já está nos favoritos"}), 400

    # Adiciona o navigation_id aos favoritos do cliente
    clientes.update_one(
        {"_id": ObjectId(id_cliente)},
        {"$push": {"favoritos": navigation_id}}
    )

    return jsonify({"message": "Produto adicionado aos favoritos com sucesso"}), 201



# Rota para listar os favoritos do cliente
@app.route("/clientes/<id_cliente>/favoritos", methods=["GET"])
def listar_favoritos(id_cliente):
    cliente = clientes.find_one({"_id": ObjectId(id_cliente)})
    if not cliente:
        return jsonify({"erro": "Cliente não encontrado"}), 404

    # Recupera os navigation_ids dos favoritos
    favoritos_ids = cliente.get("favoritos", [])
    if not favoritos_ids:
        return jsonify({"message": "Nenhum navigation ID nos favoritos"}), 200

    # Encontra os detalhes dos navigation_ids
    produtos_favoritos = []
    for navigation_id in favoritos_ids:
        produto = produtos.find_one({"navigation_id": navigation_id})
        if produto:
            produtos_favoritos.append({
                "navigation_id": produto["navigation_id"],
                "nome": produto.get("nome"),
                "preco": produto.get("preco"),
            })

    return jsonify(produtos_favoritos), 200



# Rota para exclusão dos itens nos favoritos
@app.route("/clientes/<id_cliente>/favoritos/<navigation_id>", methods=["DELETE"])
def remover_favorito(id_cliente, navigation_id):
    cliente = clientes.find_one({"_id": ObjectId(id_cliente)})
    if not cliente:
        return jsonify({"erro": "Cliente não encontrado"}), 404

    # Verifica se o navigation_id está nos favoritos
    if "favoritos" not in cliente or navigation_id not in cliente["favoritos"]:
        return jsonify({"erro": "Navigation ID não encontrado nos favoritos"}), 404

    # Remove o navigation_id dos favoritos
    clientes.update_one(
        {"_id": ObjectId(id_cliente)},
        {"$pull": {"favoritos": navigation_id}}
    )

    return jsonify({"message": "Navigation ID removido dos favoritos com sucesso"}), 200





if __name__ == '__main__':
    app.run(debug=True)

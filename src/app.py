from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

#Configuração inicial do Flask
@app.route('/')
def home():
    return "Flask configurado com sucesso!"

#Configuração inicial do MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client['api_db']
clientes = db['clientes']

#Rota de conexão com o MongoDB
@app.route('/test-db')
def test_db():
    try:
        db.command("ping")
        return "Conexão com o MongoDB estabelecida com sucesso!"
    except Exception as e:
        return f"Erro ao conectar ao MongoDB: {e}"

#Rota para criar clientes
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



#Rota para listar os clientes cadastrados na API
@app.route("/clientes", methods=["GET"])
def list_customers():
    listar_clientes = [
        {**cliente, "_id": str(cliente["_id"])}
        for cliente in clientes.find()
    ]
    return jsonify(listar_clientes), 200



#Atualização de cadastro de clientes
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



#Exclusão de cadastro de clientes
@app.route("/clientes/<id_cliente>", methods=["DELETE"])
def deletar_clientes(id_cliente):
    result = clientes.delete_one({"_id": ObjectId(id_cliente)})
    if result.deleted_count == 0:
        return jsonify({"erro": "Cliente não encontrado"}), 404
    return jsonify({"message": "Cliente deletado com sucesso"}), 200





if __name__ == '__main__':
    app.run(debug=True)

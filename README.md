# API Flask - Gerenciamento de Clientes e Produtos

Este projeto contém uma API em Flask que gerencia um catálogo de produtos e permite a interação com dados de clientes. A API se conecta ao MongoDB para armazenar informações sobre clientes, produtos e favoritos.

## Funcionalidades

- **Gerenciamento de Clientes:**
  - Criar, editar e excluir clientes.
  - Login e logout de clientes.
  - Visualizar todos os clientes cadastrados ou um cliente específico.

- **Gerenciamento de Produtos:**
  - Criar, editar e excluir produtos.
  - Listar todos os produtos ou um produto específico.
  - Buscar produtos por `navigation_id`.

- **Favoritos:**
  - Adicionar produtos aos favoritos de um cliente.
  - Listar os favoritos de um cliente.
  - Remover produtos dos favoritos.

## Requisitos

- Python 3.x
- Flask
- pymongo
- requests
- bson

## Instalação

1. Clone o repositório:

   `git clone <URL-do-repositório>`

2. Instale as dependências:

   Se você estiver usando um ambiente virtual:

   `python -m venv venv`  
   `source venv/bin/activate`  # No Windows use: `.\\venv\\Scripts\\activate`  
   `pip install -r requirements.txt`

3. Configure o MongoDB localmente (caso não tenha um MongoDB em execução):

   - Instale o MongoDB seguindo a documentação oficial (https://www.mongodb.com/try/download/community).
   - Inicie o serviço MongoDB com:

     `mongod`

4. Execute a aplicação Flask:

   `python app.py`

5. A API estará rodando em `http://localhost:5000`.

## Endpoints da API

### Clientes

- **Criar Cliente (POST /clientes)**

  Cria um novo cliente. Os campos obrigatórios são `nome`, `email` e `senha`.

- **Listar Clientes (GET /clientes)**

  Lista todos os clientes cadastrados.

- **Editar Cliente (PUT /clientes/<id_cliente>)**

  Edita um cliente existente. É necessário passar ao menos um dos campos: `nome`, `email` ou `senha`.

- **Deletar Cliente (DELETE /clientes/<id_cliente>)**

  Exclui um cliente.

- **Login (POST /login)**

  Realiza o login do cliente. Os campos obrigatórios são `email` e `senha`.

- **Visualizar Cliente (GET /login)**

  Retorna os detalhes do cliente logado ou todos os clientes cadastrados.


### Produtos

- **Criar Produto (POST /produtos)**

  Cria um novo produto. Os campos obrigatórios são `title`, `price`, `description`, `image`, `brand` e `navigation_id`.

- **Listar Produtos (GET /produtos)**

  Lista todos os produtos ou um produto específico, podendo buscar por `navigation_id`.

- **Editar Produto (PUT /produtos/<id_produto>)**

  Edita um produto existente. É necessário passar pelo menos um dos campos: `title`, `price`, `description`, `image` ou `brand`.

- **Deletar Produto (DELETE /produtos/<id_produto>)**

  Exclui um produto.

### Favoritos

- **Adicionar Favorito (POST /clientes/<id_cliente>/favoritos)**

  Adiciona um produto aos favoritos de um cliente.

- **Listar Favoritos (GET /clientes/<id_cliente>/favoritos)**

  Lista todos os produtos favoritados de um cliente.

- **Remover Favorito (DELETE /clientes/<id_cliente>/favoritos/<navigation_id>)**

  Remove um produto dos favoritos de um cliente.

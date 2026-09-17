from flask import Flask, request, jsonify
from flasgger import Swagger
from flask_cors import CORS
from datetime import datetime
from database import db
from models import Itens, Veiculos
from werkzeug.exceptions import NotFound

app = Flask(__name__)

# Configuração do banco de dados SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///manutencao.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app, resources={r"/*": {"origins": "*"}})
swagger = Swagger(app)

# Inicializa o banco de dados
db.init_app(app)

# Criar o banco de dados
with app.app_context():
    db.create_all()

# Rota para recuperar os registros
@app.route('/recuperar', methods=['GET'])
def recuperar():
    '''Retorna todo o banco de dados cadastrado.
    ---
    tags:
      - geral
    responses:
      200:
        description: Registros lidos com sucesso.
    '''

    itens= [item.to_dict() for item in Itens.query.all()]
    veiculo = [veiculo.to_dict() for veiculo in Veiculos.query.all()]
    
    return jsonify({'veiculo':veiculo,
                    'itens':itens})


# Rota para salvar novo item de manutenção
@app.route('/salvar-item', methods=['POST', 'OPTIONS'])
def salvar_item():

    '''Salva novo item de manutenção no banco de dados
    ---
    consumes:
      - application/json
    tags:
      - Ítens de manutenção
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            descricao:
              type: string
              example: Óleo do motor
            intervalo_km:
              type: integer
              example: 10000
            intervalo_prazo:
              type: integer
              example: 12
            ultima_troca_km:
              type: integer
              example: 10000
            ultima_troca_data:
              type: string
              format: date
              example: "2023-12-04"
            veiculo:
              type: int
              example: 1
    responses:
      201:
        description: id do registro salvo
        
    '''
    if request.method == 'OPTIONS':
      return {},200
    
    dados_recebidos = request.json
    novo_registro = Itens(
        descricao=dados_recebidos.get('descricao'),
        intervalo_km=dados_recebidos.get('intervalo_km'),
        intervalo_prazo=dados_recebidos.get('intervalo_prazo'),
        ultima_troca_km=dados_recebidos.get('ultima_troca_km'),
        ultima_troca_data=datetime.strptime(dados_recebidos['ultima_troca_data'],
                                            '%Y-%m-%d').date(),
        veiculo=dados_recebidos.get('veiculo'),
    )
    db.session.add(novo_registro)
    db.session.commit()
    return jsonify({'id':novo_registro.id}), 201


# Rota para editar item dew manutenção
@app.route('/alterar-item/<int:id>', methods=['PUT'])
def alterar_item(id):
    '''Altera um item de manutenção no banco de dados
    ---
    consumes:
      - application/json
    tags:
      - Ítens de manutenção
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID do item
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            descricao:
              type: string
              example: Óleo do motor
            intervalo_km:
              type: integer
              example: 10000
            intervalo_prazo:
              type: integer
              example: 12
            ultima_troca_km:
              type: integer
              example: 10000
            ultima_troca_data:
              type: string
              format: date
              example: "2023-12-04"
            veiculo:
              type: int
              example: 1
    responses:
      200:
        description: Registro atualizado com sucesso!
      404: 
        description: Registro não encontrado!
    '''
    
    dados_recebidos = request.json
    try:
        registro = Itens.query.get_or_404(id)
    except NotFound:
        return jsonify({"404": "Item não encontrado"}), 404
        

    registro.descricao = dados_recebidos.get('descricao', registro.descricao)
    registro.intervalo_km = dados_recebidos.get('intervalo_km', registro.intervalo_km)
    registro.intervalo_prazo = dados_recebidos.get('intervalo_prazo', registro.intervalo_prazo)
    registro.ultima_troca_km = dados_recebidos.get('ultima_troca_km', registro.ultima_troca_km)
    registro.ultima_troca_data = datetime.strptime(dados_recebidos['ultima_troca_data'],
                                          '%Y-%m-%d').date()
    registro.veiculo = dados_recebidos.get('veiculo', registro.veiculo)
    db.session.commit()
    return jsonify({'200': 'Registro atualizado com sucesso!'})


# Rota para deletar item de manutenção
@app.route('/deletar-item/<int:id>', methods=['DELETE', 'OPTIONS'])
#@cross_origin()
def deletar_item(id):
    '''Deleta o registro no banco de dados
    ---
    consumes:
      - application/json
    tags:
      - Ítens de manutenção
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID do item

    responses:
      200:
        description: Registro deletado com sucesso!
      404:
        description: Registro não encontrado!
    '''
    if request.method == 'OPTIONS':
        return {}, 200
    try:
        registro = Itens.query.get_or_404(id)
    except NotFound:
        return jsonify({"404": "Item não encontrado"}), 404
        
    db.session.delete(registro)
    db.session.commit()
    return jsonify({'mensagem': 'Registro deletado com sucesso!'})

# Rota para salvar novo veiculo
@app.route('/salvar-veiculo', methods=['POST', 'OPTIONS'])
def salvar_veiculo():

    '''Salva novo veiculo no banco de dados
    ---
    consumes:
      - application/json
    tags:
      - Veículos
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            descricao:
              type: string
              example: Nissan Versa
    responses:
      201:
        description: id do registro salvo
    '''
    
    if request.method == 'OPTIONS':
      return {},200
        
    dados_recebidos = request.json
    novo_registro = Veiculos(
        descricao=dados_recebidos.get('descricao'),
    )
    db.session.add(novo_registro)
    db.session.commit()
    return jsonify({'id':novo_registro.id}), 201

# Rota para editar veiculo
@app.route('/alterar-veiculo/<int:id>', methods=['PUT'])
def alterar_veiculo(id):
    '''Altera um veiculo no banco de dados
    ---
    consumes:
      - application/json
    tags:
      - Veículos
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID do veículo
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            descricao:
              type: string
              example: Ferrari F40
    responses:
      200:
        description: Registro atualizado com sucesso!
      404:
        description: Registro não encontrado
    '''

    dados_recebidos = request.json
    try:
      registro = Veiculos.query.get_or_404(id)
    except NotFound:
        return jsonify({"404": "Item não encontrado"}), 404
    
    registro.descricao = dados_recebidos.get('descricao', registro.descricao)
    db.session.commit()
    return jsonify({'mensagem': 'Registro atualizado com sucesso!'})

# Rota para deletar registro
@app.route('/deletar-veiculo/<int:id>', methods=['DELETE'])
def deletar_veiculo(id):
    '''Deleta o registro no banco de dados
    ---
    consumes:
      - application/json
    tags:
      - Veículos
    parameters:
      - name: id
        in: path
        type: integer
        required: true
        description: ID do item

    responses:
      200:
        description: Registro deletado com sucesso!
      404:
        description: Registro não encontrado!
      500:
        description: Registro associado a uma chave estrangeira

    '''
    try:
        registro = Veiculos.query.get_or_404(id)
    except NotFound:
        return jsonify({"404": "Item não encontrado"}), 404
    
    try:
        db.session.delete(registro)
        db.session.commit()
        return jsonify({'200': 'Registro deletado com sucesso!'})
    
    except:
        db.session.rollback()
        return jsonify({"500": "Registro associado a uma chave estrangeira"}), 500

if __name__ == '__main__':
    app.run(debug=True)

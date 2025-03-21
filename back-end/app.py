from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

# Connect to MySQL (adjust the database name to match yours)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="predistock_db",  # match your .sql
    charset='utf8' # supports accents like in "descrição"
)
cursor = db.cursor()

@app.route('/api/add-product', methods=['POST'])
def add_product():
    data = request.get_json()

    nome = data.get('nome')
    descricao = data.get('descricao')
    preco = float(data.get('preco', 0))
    quantidade = int(data.get('quantidade', 0))
    categoria_id = int(data.get('categoria_id', 0))

    # Check if fields are valid
    if not nome or preco <= 0 or quantidade <= 0 or categoria_id <= 0:
        return jsonify({'error': 'Preencha todos os campos corretamente.'}), 400

    try:
        query = """
            INSERT INTO produtos (nome, descrição, preço, quantidade, categoria_id)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (nome, descricao, preco, quantidade, categoria_id))
        db.commit()
        return jsonify({'message': 'Produto adicionado com sucesso!'}), 200

    except Exception as e:
        print("Erro:", e)
        return jsonify({'error': 'Erro ao adicionar produto.'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)


from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your_secret_key'

# Connect to MySQL (adjust the database name to match yours)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="predistock_db",
    charset='utf8'
)
cursor = db.cursor()

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = generate_password_hash(data.get('password'), method='sha256')

    try:
        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        cursor.execute(query, (username, password))
        db.commit()
        return jsonify({'message': 'User registered successfully!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    try:
        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user[2], password):
            token = jwt.encode({'user_id': user[0], 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)}, app.config['SECRET_KEY'])
            return jsonify({'token': token}), 200
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/add-product', methods=['POST'])
def add_product():
    token = request.headers.get('Authorization').split()[1]
    data = request.get_json()

    try:
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        user_id = decoded_token['user_id']

        nome = data.get('nome')
        descricao = data.get('descricao')
        preco = float(data.get('preco', 0))
        quantidade = int(data.get('quantidade', 0))
        categoria_id = int(data.get('categoria_id', 0))

        if not nome or preco <= 0 or quantidade <= 0 or categoria_id <= 0:
            return jsonify({'error': 'Preencha todos os campos corretamente.'}), 400

        query = """
            INSERT INTO produtos (nome, descrição, preço, quantidade, categoria_id, user_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (nome, descricao, preco, quantidade, categoria_id, user_id))
        db.commit()
        return jsonify({'message': 'Produto adicionado com sucesso!'}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)


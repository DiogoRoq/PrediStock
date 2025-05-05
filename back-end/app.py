from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib
import os

app = Flask(__name__)
CORS(app)


db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'salesinv',
    'charset': 'utf8'
}


model_path = 'trained_demand_model.pkl'
model_trained = False

from sklearn.preprocessing import LabelEncoder

@app.route('/train-model', methods=['POST'])
def train_model_from_db():
    global model_trained
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)  

        cursor.execute("SELECT * FROM sample_500_with_product_names")
        rows = cursor.fetchall()
        df = pd.DataFrame(rows)
        print("🔍 DataFrame Columns:", df.columns.tolist())
        print("🧪 Sample Row:\n", df.head(1).to_dict())


        if df.empty:
            return jsonify({'status': 'error', 'message': 'No data found'})

        
        df['week'] = pd.to_datetime(df['week'], format="%d/%m/%y")
        df['week_number'] = df['week'].dt.isocalendar().week
        df['year'] = df['week'].dt.year

        
        le = LabelEncoder()
        df['product_name_encoded'] = le.fit_transform(df['product_name'])

        
        joblib.dump(le, 'label_encoder.pkl')
    
        features = [
            'store_id', 'sku_id', 'week_number', 'year',
            'base_price', 'is_featured_sku', 'is_display_sku', 'product_name_encoded'
        ]
        X = df[features]
        y = df['units_sold']

        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)

        joblib.dump(model, model_path)
        model_trained = True

        return jsonify({'status': 'success', 'message': 'Model trained with product_name included'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/model-status', methods=['GET'])
def get_model_status():
    return jsonify({'trained': model_trained})

@app.route('/predict-demand', methods=['GET'])
def predict_demand():
    global model_trained
    if not model_trained or not os.path.exists(model_path):
        return jsonify({'error': 'Model not trained yet'})

    model = joblib.load(model_path)
    le = joblib.load('label_encoder.pkl')

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM sample_150_test_with_product_names")
        rows = cursor.fetchall()
        df = pd.DataFrame(rows)

        df['week'] = pd.to_datetime(df['week'], format='%y/%m/%d')
        df['week_number'] = df['week'].dt.isocalendar().week
        df['year'] = df['week'].dt.year
        df['product_name_encoded'] = le.transform(df['product_name'])

        features = [
            'store_id', 'sku_id', 'week_number', 'year',
            'base_price', 'is_featured_sku', 'is_display_sku', 'product_name_encoded'
        ]
        X_pred = df[features]

        predictions = model.predict(X_pred)
        df['predicted_units_sold'] = predictions.round(2)
        df['week'] = df['week'].dt.strftime('%Y-%m-%d')

        return jsonify(df.to_dict(orient='records'))

    except Exception as e:
        return jsonify({'error': str(e)}), 500





@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = generate_password_hash(data.get('password'), method='sha256')

    try:
        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        cursor.execute(query, (username, password))
        db_config.commit()
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
        db_config.commit()
        return jsonify({'message': 'Produto adicionado com sucesso!'}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)


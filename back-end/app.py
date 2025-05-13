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
        # Establish database connection and create a cursor
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Insert user data into the database
        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        cursor.execute(query, (username, password))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({'message': 'User registered successfully!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    try:
        # Establish database connection and create a cursor
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Query user data from the database
        query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and check_password_hash(user[2], password):
            token = jwt.encode(
                {'user_id': user[0], 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)},
                app.config['SECRET_KEY'],
                algorithm='HS256'
            )
            return jsonify({'token': token}), 200
        else:
            return jsonify({'message': 'Invalid username or password'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/add-product', methods=['POST'])
def add_product():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization token is missing'}), 401

    token = token.split()[1]  # Extract the token from the "Bearer <token>" format
    data = request.get_json()

    try:
        # Decode the token to get the user ID
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        user_id = decoded_token['user_id']

        # Retrieve and validate input data
        record_id = data.get('record_ID')
        store_id = data.get('store_id')
        sku_id = data.get('sku_id')
        product_name = data.get('product_name')
        total_price = float(data.get('total_price', 0))
        base_price = float(data.get('base_price', 0))
        units_sold = int(data.get('units_sold', 0))
        is_featured_sku = 1 if data.get('is_featured_sku', False) else 0
        is_display_sku = 1 if data.get('is_display_sku', False) else 0
        week = datetime.datetime.now().strftime('%d/%m/%y')  # Default to current date

        # Validation for required fields
        if not all([record_id, store_id, sku_id, product_name]) or total_price <= 0 or base_price <= 0:
            return jsonify({'error': 'Preencha todos os campos corretamente.'}), 400

        # Establish database connection and create a cursor
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Insert product data into `sample_500_with_product_names`
        query_500 = """
            INSERT INTO sample_500_with_product_names 
            (record_ID, week, store_id, sku_id, product_name, total_price, base_price, 
            is_featured_sku, is_display_sku, units_sold) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query_500, (
            record_id, week, store_id, sku_id, product_name, total_price, base_price, 
            is_featured_sku, is_display_sku, units_sold
        ))

        # Insert product data into `sample_150_with_product_names` (without units_sold)
        query_150 = """
            INSERT INTO sample_150_with_product_names 
            (record_ID, week, store_id, sku_id, product_name, total_price, base_price, 
            is_featured_sku, is_display_sku) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query_150, (
            record_id, week, store_id, sku_id, product_name, total_price, base_price, 
            is_featured_sku, is_display_sku
        ))

        # Commit the transaction
        conn.commit()

        # Close database resources
        cursor.close()
        conn.close()

        return jsonify({'message': 'Produto adicionado com sucesso!'}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except mysql.connector.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/graph-demand-data', methods=['GET'])
def graph_demand_data():
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

        # Prepare data
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

        response = df[['week', 'predicted_units_sold']].groupby('week').sum().reset_index()
        return jsonify(response.to_dict(orient='records'))

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/graph-sales-history', methods=['GET'])
def graph_sales_history():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT week, units_sold FROM sample_500_with_product_names")
        rows = cursor.fetchall()
        df = pd.DataFrame(rows)

        # Prepare data
        df['week'] = pd.to_datetime(df['week'], format='%y/%m/%d')
        df['week'] = df['week'].dt.strftime('%Y-%m-%d')

        response = df.groupby('week').sum().reset_index()
        return jsonify(response.to_dict(orient='records'))

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)


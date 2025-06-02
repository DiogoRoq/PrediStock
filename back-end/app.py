from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta, timezone
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import joblib
import os

app = Flask(__name__)
app.secret_key = '91a0da2ffd8ae6a6d4349248d56d677bf30566cc8a873f9fa09d03e6c14beb0a'
CORS(app, resources={r"/*": {"origins": "*"}}, allow_headers="*", methods=["GET", "POST", "OPTIONS"], supports_credentials=True)


db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'salesinv',
    'charset': 'utf8'
}

model_path = 'trained_demand_model.pkl'
model_trained = False



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





@app.route('/api/add-product', methods=['POST'])
def add_product():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Authorization token is missing'}), 401

    token = token.split()[1]  # Extract the token from the "Bearer <token>" format
    data = request.get_json()

    try:
        # Decode the token to get the user ID
        decoded_token = jwt.decode(token, app.secret_key, algorithms=["HS256"])
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
        week = datetime.now().strftime('%d/%m/%y')  # Default to current date

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
            INSERT INTO sample_150_test_with_product_names 
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
    sku = request.args.get('sku')
    if not sku:
        return jsonify({'error': 'SKU ID is required'}), 400

    global model_trained
    if not model_trained or not os.path.exists(model_path):
        return jsonify({'error': 'Model not trained yet'})

    try:
        model = joblib.load(model_path)
        le = joblib.load('label_encoder.pkl')

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM sample_150_test_with_product_names WHERE sku_id = %s", (sku,))
        rows = cursor.fetchall()
        conn.close()

        df = pd.DataFrame(rows)
        if df.empty:
            return jsonify([])

        df['week'] = pd.to_datetime(df['week'], format='%y/%m/%d')
        today = datetime.today()
        df = df[df['week'] > today]
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
    sku = request.args.get('sku')
    if not sku:
        return jsonify({'error': 'SKU ID is required'}), 400

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT week, units_sold 
            FROM sample_500_with_product_names
            WHERE sku_id = %s
        """, (sku,))
        rows = cursor.fetchall()
        conn.close()

        df = pd.DataFrame(rows)
        if df.empty:
            return jsonify([])

        df['week'] = pd.to_datetime(df['week'], format='%y/%m/%d')
        cutoff_date = datetime.strptime("2025-01-01", "%Y-%m-%d")
        df = df[df['week'] <= cutoff_date]
        df['week'] = df['week'].dt.strftime('%Y-%m-%d')
        

        response = df.groupby('week').sum().reset_index()
        return jsonify(response.to_dict(orient='records'))

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products')
def get_products():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT DISTINCT sku_id, product_name FROM sample_500_with_product_names ORDER BY product_name")
        rows = cursor.fetchall()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/inventory')
def get_inventory():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT sku_id, product_name, units_sold, base_price, total_price, week, store_id
            FROM sample_500_with_product_names
            ORDER BY product_name
        """)
        rows = cursor.fetchall()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([username, email, password]):
        return jsonify({'status': 'error', 'message': 'All fields are required'}), 400

    hashed_password = generate_password_hash(password)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                       (username, email, hashed_password))
        conn.commit()
        return jsonify({'status': 'success', 'message': 'User registered successfully'})
    except mysql.connector.IntegrityError:
        return jsonify({'status': 'error', 'message': 'User already exists'}), 409
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if user and check_password_hash(user['password_hash'], password):
            token = jwt.encode({
                'user_id': user['id'],
                'exp': datetime.now(timezone.utc) + timedelta(hours=24)
            }, app.secret_key, algorithm='HS256')
            return jsonify({'status': 'success', 'token': token})
        return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401
    finally:
        cursor.close()
        conn.close()

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get('email')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone() is None:
            return jsonify({'status': 'error', 'message': 'Email not found'}), 404

        token = os.urandom(16).hex()
        expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
        cursor.execute("UPDATE users SET reset_token = %s, reset_token_expiry = %s WHERE email = %s",
                       (token, expiry, email))
        conn.commit()
        return jsonify({'status': 'success', 'reset_token': token})
    finally:
        cursor.close()
        conn.close()

@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    token = data.get('token')
    new_password = data.get('new_password')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE reset_token = %s AND reset_token_expiry > NOW()", (token,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'status': 'error', 'message': 'Invalid or expired token'}), 400

        hashed_password = generate_password_hash(new_password)
        cursor.execute("UPDATE users SET password_hash = %s, reset_token = NULL, reset_token_expiry = NULL WHERE reset_token = %s",
                       (hashed_password, token))
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Password reset successful'})
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    app.run(debug=True, port=5000)
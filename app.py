import psycopg2
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import jwt
import bcrypt
import time

app = Flask(__name__)
app.secret_key = 'DgXJEBahOw7iFn6z4Xu9AABjqTdj7NO-jH7QwUhmTOBXvHiSVvLE38zL53z3paeRRny3eIl5bFZgcYgX4RBZLQ'

def generate_token(username):
    
    expiration_time = time.time() +  10 
    payload = {'username': username, 'exp': expiration_time}
    return jwt.encode(payload, app.secret_key, algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, app.secret_key, algorithms=['HS256'])
        if time.time() > payload['exp']:
            return None  
        else:
            return payload['username']
    except jwt.ExpiredSignatureError:
        return None 
    except jwt.InvalidTokenError:
        return None 

def create_connection():
    try:
        conn = psycopg2.connect(
            database="form_data",
            host="localhost",
            user="postgres",
            password="udhaya",
            port="7000"  
        )
        return conn
    except psycopg2.Error as e:
        print("Error connecting to PostgreSQL database:", e)
        return None 
    
table_name = "contact_data"

def table_create():
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS {} (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                age INT,
                email VARCHAR(100),
                message VARCHAR(100)
            );
        '''.format(table_name)
        create_register_table_query = '''
            CREATE TABLE IF NOT EXISTS Register (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100),
                password VARCHAR(100)
            );
        '''
        
        cursor.execute(create_table_query)
        cursor.execute(create_register_table_query)
        conn.commit()

        cursor.close()
        conn.close()
        print("Table created")
    else:
        print("Database not connected")
table_create()

def get_user_by_username(username):
    conn = create_connection()
    cursor = conn.cursor()
    query = 'SELECT * FROM Register WHERE username = %s'
    cursor.execute(query, (username,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data
# this is starting route

@app.route('/')
def hello():
    token = session.get('token')
    if token:
        username = verify_token(token)
        if username:
            return render_template("index.html")
    return redirect(url_for('login'))


@app.route('/submit_form', methods=['POST'])
def submit_form():
    token = session.get('token')
    if not token:
        return redirect(url_for('login'))
    else:
        data = request.json
        name = data.get('name')
        age = data.get('age')
        email = data.get('email')
        message = data.get('message')
        conn = create_connection()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM {} WHERE email = %s".format(table_name), (email,))
            existing_user = cursor.fetchone()
            if existing_user:
                cursor.close()
                conn.close()
                return jsonify({"message": "This email is already stored."})
            else:
                query = "INSERT INTO {} (name, age, email, message) VALUES (%s, %s, %s, %s)".format(table_name)
                cursor.execute(query, (name, age, email, message))
                conn.commit()
                cursor.close()
                conn.close()
                print("Data saved")
                return jsonify({"message": "Data stored successfully"})
        else:
            return jsonify({"error": "Failed to connect to the database"})
    
def get_user_data(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    query = 'SELECT * FROM {} WHERE id = %s'.format(table_name)
    cursor.execute(query, (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    return user_data

@app.route('/user/<int:user_id>',methods=['GET'])
def user(user_id):
    token = session.get('token')
    if not token:
        return redirect(url_for('login'))
    else:
        username = verify_token(token)
        if not username:
            return redirect(url_for('login'))
        else:
            user_data = get_user_data(user_id)
            if user_data:
                user_dict = {
                    'id': user_data[0],
                    'name': user_data[1],
                    'age': user_data[2],
                    'email': user_data[3],
                    'message': user_data[4]
                }
                return jsonify(user_dict)
            else:
                return jsonify({'error': 'User not found'}), 404

def get_all_users():
    conn = create_connection()
    cursor = conn.cursor()
    query = 'SELECT * FROM {}'.format(table_name)
    cursor.execute(query)
    users_data = cursor.fetchall()
    conn.close()
    return users_data

@app.route('/data',methods=['GET'])
def users():
    token = session.get('token')
    if not token:
        return redirect(url_for('login'))
    else:
        username = verify_token(token)
        if not username:
            return redirect(url_for('login'))
        else:
            users_data = get_all_users()
            if users_data:
                users_list = []
                for user_data in users_data:
                    user_dict = {
                        'id': user_data[0],
                        'name': user_data[1],
                        'age': user_data[2],
                        'email': user_data[3],
                        'message': user_data[4]
                    }
                    users_list.append(user_dict)
                return jsonify(users_list)
            else:
                return jsonify([]) 

@app.route('/all')
def all():
    token = session.get('token')
    if not token:
        return redirect(url_for('login'))
    else:
        username = verify_token(token)
        if not username:
            return redirect(url_for('login'))
        else:
            return render_template("all_data.html")

@app.route('/registers')
def register():
    return render_template("register.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/registers_submit', methods=['POST'])
def registers_submit():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    conn = create_connection()
    if conn is not None:  
        cursor = conn.cursor()
    
        cursor.execute("SELECT * FROM Register WHERE username = %s", (username,))
        existing_user = cursor.fetchone()
    
        if existing_user:
            cursor.close()
            conn.close()
            return jsonify({"message": "This username is already stored."})
        else:
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            hashed_password_str = hashed_password.decode('utf-8')
            
            query = "INSERT INTO Register (username, password) VALUES (%s, %s)"
            cursor.execute(query, (username, hashed_password_str))
            conn.commit()
    
            cursor.close()
            conn.close()
    
            print("Data saved")
            return jsonify({"message": "Data stored successfully"})
    
    else:
        return jsonify({"error": "Failed to connect to the database"})

@app.route('/login1', methods=['POST'])
def login1():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user_data = get_user_by_username(username)
    if user_data and bcrypt.checkpw(password.encode(), user_data[2].encode()):
        token = generate_token(username)
        session['token'] = token
        return jsonify({"message": "Login successful"})
    else:
        return jsonify({"message": "Invalid username or password"})
    
   
@app.route('/protected_route', methods=['GET'])
def protected_route():
    token = session.get('token')
    if token:
        username = verify_token(token)
        if username:
            return jsonify({"message": "Access granted"})
        else:
            return jsonify({"error": "Invalid or expired token"}), 401
    else:
        return jsonify({"error": "Token missing"}), 401



if __name__ == '__main__':
    app.run(debug=True, port=4000)

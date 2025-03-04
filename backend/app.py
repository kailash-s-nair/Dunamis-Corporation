from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mysqldb import MySQL
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.security import check_password_hash

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'Kailash'
app.config['MYSQL_PASSWORD'] = 'dunamis'
app.config['MYSQL_DB'] = 'dunamis_db'
app.config['JWT_SECRET_KEY'] = '916ae4943193913282abcff1fefe094bfaceb6b6f016fad7489362ac43c8fbd6'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
jwt = JWTManager(app)

@app.route('/test_db')
def test_db():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT 1")
        return "Database connection successful!"
    except Exception as e:
        return f"Database connection failed: {str(e)}", 500

# User Registration
@app.route('/register', methods=['POST'])  #  Changed route
def register():
    try:
        data = request.json
        hashed_password = generate_password_hash(data['password'])

        cursor = mysql.connection.cursor()
        query = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)"
        values = (data['username'], hashed_password, data['role'])

        cursor.execute(query, values)
        mysql.connection.commit()
        return jsonify({"message": "User registered!"})

    except Exception as e:
        print("Error in /register:", e)
        return jsonify({"error": str(e)}), 500


# User Login
# Add detailed error handling in your login route
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()

        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        # Verify password hash from database
        if check_password_hash(user['password'], password):
            access_token = create_access_token(identity={
                'username': user['username'],
                'role': user['role'],
                'id': user['id']
            })
            return jsonify({
                "message": "Login successful",
                "access_token": access_token
            }), 200

        return jsonify({"error": "Invalid credentials"}), 401

    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Fetch logged-in user details
@app.route('/user', methods=['GET'])
@jwt_required()
def get_user():
    current_user = get_jwt_identity()
    return jsonify(current_user), 200

# Add an item (Admin only)
@app.route('/catalogue', methods=['POST'])
@jwt_required()
def add_item():
    if get_jwt_identity()['role'] != 'admin':
        return jsonify({"message": "Access denied"}), 403
    data = request.json
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO catalogue (name, description, created_by) VALUES (%s, %s, %s)",
                   (data['name'], data['description'], get_jwt_identity()['id']))
    mysql.connection.commit()
    return jsonify({"message": "Item added!"})

# Get all items
@app.route('/catalogue', methods=['GET'])
@jwt_required()
def get_items():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, name, description FROM catalogue")
    items = cursor.fetchall()
    cursor.close()
    return jsonify(items), 200

# Delete an item (Admin only)
@app.route('/catalogue/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_item(item_id):
    if get_jwt_identity()['role'] != 'admin':
        return jsonify({"message": "Access denied"}), 403
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM catalogue WHERE id=%s", (item_id,))
    mysql.connection.commit()
    return jsonify({"message": "Item deleted!"})

if __name__ == '__main__':
    app.run(debug=True)
#   import secrets
#   print(secrets.token_hex(32))
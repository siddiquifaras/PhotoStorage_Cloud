from flask import Flask, jsonify, request
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'phovinologin.mysql.database.azure.com'
app.config['MYSQL_USER'] = 'phovinouser'
app.config['MYSQL_PASSWORD'] = 'Alpha12-'
app.config['MYSQL_DB'] = 'phovinodb'

mysql = MySQL(app)


@app.route('/')
def index():
    return "HELLO WORLD"


@app.route('/login', methods=['POST'])
def login_user():
    # Get user data from the request body
    user_data = request.get_json()

    if 'email' not in user_data or 'password' not in user_data or 'username' not in user_data:
        return jsonify({'status': 'failure', 'message': 'Missing required fields'}), 400

    email = user_data['email']
    password = user_data['password']
    username=user_data['username']

    # Validate user credentials against the database
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user WHERE email = %s AND password = %s AND username= %s", (email, password, username))
    user = cur.fetchone()
    cur.close()

    if user:
        return jsonify({'status': 'success', 'message': 'User logged in successfully'}), 200
    else:
        return jsonify({'status': 'failure', 'message': 'Invalid credentials'}), 401


if __name__ == '__main__':
    app.run(debug=True)

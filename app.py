from flask import Flask, jsonify, redirect, url_for, request, session, flash
from flask_mysqldb import MySQL, MySQLdb
import bcrypt
import werkzeug
import re

app = Flask(__name__)
mysql = MySQL(app)
app.secret_key = "membuatLoginFlask"

app.config["MYSQL_HOST"] = 'localhost'
app.config["MYSQL_USER"] = 'root'
app.config["MYSQL_PASSWORD"] = ''
app.config["MYSQL_DB"] = 'projectbangkit'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

@app.route('/register', methods =['GET', 'POST'])
def register():
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE Email = % s', (email, ))
        account = cursor.fetchone()
        if account:
                return jsonify({"error": True, "message": "Email Sudah Ada!!"})
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                return jsonify({"error": True, "message": "Mohon isi format email yang benar!!"})
        elif not name or not password or not email:
                return jsonify({"error": True, "message": "Mohon lengkapi data anda!!"})
        else:
            cursor.execute('INSERT INTO users VALUES (NULL, % s, % s, % s)', (name, email, hash_password, ))
            mysql.connection.commit()
            return jsonify({"error": False, "message": "Registrasi berhasil!!"})


@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        input_password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = % s ', (email, ))
        if cursor is not None:
                account = cursor.fetchone()
                passwords = account['Password']
                if bcrypt.checkpw(input_password.encode('utf-8'),passwords.encode('utf-8')):
                        session['loggedin'] = True
                        session['id'] = account['ID']
                        session['email'] = account['Email']
                        return jsonify({"error": False, "message": "Login Berhasil!!"})
                        cursor.close()
                else:
                        return jsonify({"error": True, "message": "Login Gagal!!"})

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)
    return jsonify({"error": False, "message": "Logout Berhasil!!"})
#     return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

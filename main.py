from flask import Flask, request, make_response, jsonify
from coba1 import predict, prediksi, findmax
from flask_mysqldb import MySQL, MySQLdb
import bcrypt, re

app = Flask(__name__)
mysql = MySQL(app)
app.secret_key = "khususPeduliBicara"

app.config["MYSQL_HOST"] = '10.83.48.4'
app.config["MYSQL_USER"] = 'admin'
app.config["MYSQL_PASSWORD"] = 'ps108'
app.config["MYSQL_DB"] = 'pedulibicara'
app.config['MYSQL_UNIX_SOCKET'] = "/cloudsql/pedulibicara-352415:us-central1:pedulibicara1"
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

@app.route('/model', methods=['GET', 'POST'])
def peduli_bicara():
    if request.method == 'POST':
        # Mengambil data dari upload
        audio = request.files['file']
        prosesdata = predict(audio)
        hasil = prediksi(prosesdata)
        return make_response(jsonify(findmax(hasil)),200)


@app.route('/register', methods =['GET', 'POST'])
def register():
        ortuname = request.form['ortuname']
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
            cursor.execute('INSERT INTO users VALUES (NULL, %s, % s, % s, % s)', (ortuname, name, email, hash_password, ))
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
                        return jsonify({"error": False, "message": "Login Berhasil!!"})
                else:
                        return jsonify({"error": True, "message": "Login Gagal!!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
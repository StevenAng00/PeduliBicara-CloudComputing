from flask import Flask, request
from pedulibicaraML import prediksi

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def peduli_bicara():
    if request.method == 'POST':
        # Mengambil data dari upload
        audio = request.files['file']
        penilaian = prediksi(audio)
        return(hasil==penilaian)

if __name__ == '__main__':
    app.run(debug=True)
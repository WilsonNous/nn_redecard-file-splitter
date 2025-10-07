from flask import Flask, render_template, request, send_file
import os
from split_redecard import process_file

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if not file:
        return "Nenhum arquivo enviado", 400
    path_in = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path_in)
    
    outputs = process_file(path_in, OUTPUT_FOLDER)
    
    return f"Processado com sucesso! {len(outputs)} arquivos gerados em {OUTPUT_FOLDER}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

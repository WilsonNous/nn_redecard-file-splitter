from flask import Flask, render_template, request, send_file
import os
import zipfile
import io
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
    uploaded_files = request.files.getlist('file')
    if not uploaded_files:
        return "Nenhum arquivo enviado.", 400

    all_generated = []

    for file in uploaded_files:
        filename = file.filename
        path_in = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path_in)
        generated = process_file(path_in, OUTPUT_FOLDER)
        all_generated.extend(generated)

    # Gera ZIP de saída em memória
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in all_generated:
            arcname = os.path.basename(file_path)
            zipf.write(file_path, arcname)
    zip_buffer.seek(0)

    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name='resultados_rede_splitter.zip'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

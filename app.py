from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
from werkzeug.utils import secure_filename
import json

app = Flask(__name__)
CORS(app) 

# Configurações
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Criar pasta uploads se não existir
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    """Verifica se o arquivo tem extensão permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    """Verifica se a API está disponível"""
    return jsonify({
        'status': 'success',
        'message': 'API está funcionando!',
        'version': '1.0.0'
    })

@app.route('/api/uploadArquivo', methods=['POST'])
def upload_arquivo():
    """Recebe um arquivo CSV ou Excel, lê com pandas e retorna JSON"""
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado!'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Nome do arquivo inválido!'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            # Lê CSV ou Excel
            if filename.lower().endswith('.csv'):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_excel(filepath)

            # Converte para JSON
            data_json = df.to_dict(orient='records')
            return jsonify({
                'status': 'success',
                'rows': len(data_json),
                'data': data_json
            }), 200

        except Exception as e:
            return jsonify({'error': f'Erro ao processar arquivo: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Tipo de arquivo não permitido!'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

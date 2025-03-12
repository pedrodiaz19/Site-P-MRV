import os
import sqlite3
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder="static")  # Configura a pasta estática
CORS(app)  # Habilita CORS

# Configuração correta do caminho do banco de dados para o Render
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Diretório atual do backend.py
DB_PATH = os.path.join(BASE_DIR, "processos.db")  # Caminho do banco relativo

# Função para buscar processos no banco de dados
def buscar_processo(numero_processo):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT processo, vara, nome, status FROM processos WHERE processo = ?", (numero_processo,))
    resultado = cursor.fetchall()
    conn.close()

    return [{"processo": r[0], "vara": r[1], "nome": r[2], "status": r[3]} for r in resultado] if resultado else []

@app.route("/consulta", methods=["GET"])
def consulta():
    numero_processo = request.args.get("processo")
    if not numero_processo:
        return jsonify({"erro": "Número do processo é obrigatório"}), 400

    resultados = buscar_processo(numero_processo)
    return jsonify(resultados if resultados else {"erro": "Processo não encontrado"}), 404

# Rota para servir o index.html corretamente
@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")

# Rota para servir imagens da pasta "static"
@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(os.path.join(BASE_DIR, "static"), filename)

# Rodando localmente
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

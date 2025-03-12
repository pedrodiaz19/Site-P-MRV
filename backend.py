import os
from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__, static_folder="static")  
CORS(app)

# Ajusta a porta automaticamente para o Render
PORT = int(os.environ.get("PORT", 5000))

# Diretório do backend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 🔹 Servindo o index.html
@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")

# 🔹 Servindo arquivos estáticos (exemplo: imagens, CSS, JS)
@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(os.path.join(BASE_DIR, "static"), filename)

# 🔹 Rota de consulta funcionando normalmente
@app.route("/consulta", methods=["GET"])
def consulta():
    numero_processo = request.args.get("processo")
    if not numero_processo:
        return jsonify({"erro": "Número do processo é obrigatório"}), 400

    resultados = buscar_processo(numero_processo)
    return jsonify(resultados if resultados else {"erro": "Processo não encontrado"}), 404

# 🔹 Função para buscar processos no banco de dados
def buscar_processo(numero_processo):
    DB_PATH = os.path.join(BASE_DIR, "processos.db")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT processo, vara, nome, status FROM processos WHERE processo = ?", (numero_processo,))
    resultado = cursor.fetchall()
    conn.close()
    
    return [{"processo": r[0], "vara": r[1], "nome": r[2], "status": r[3]} for r in resultado] if resultado else []

# 🔹 Iniciando a aplicação
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)

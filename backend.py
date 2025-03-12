import os
import sqlite3
import re  # Biblioteca para manipulação de strings
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "processos.db")

def buscar_processo(entrada):
    """Busca um processo no banco de dados pelo número do processo ou CPF."""
    entrada_formatada = re.sub(r'[\.\-]', '', entrada)  # Remove pontos e traços

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Primeiro, tenta buscar pelo número do processo
    cursor.execute("""
        SELECT processo, vara, nome, status FROM processos 
        WHERE REPLACE(REPLACE(processo, '.', ''), '-', '') = ?
    """, (entrada_formatada,))
    resultado = cursor.fetchall()

    # Se não encontrar pelo processo, busca pelo CPF
    if not resultado:
        cursor.execute("""
            SELECT processo, vara, nome, status FROM processos 
            WHERE REPLACE(REPLACE(cpf, '.', ''), '-', '') = ?
        """, (entrada_formatada,))
        resultado = cursor.fetchall()

    conn.close()

    return [
        {"processo": r[0], "vara": r[1], "nome": r[2], "status": r[3]}
        for r in resultado
    ]

@app.route("/consulta", methods=["GET"])
def consulta():
    entrada = request.args.get("processo")
    if not entrada:
        return jsonify({"erro": "Número do processo ou CPF é obrigatório"}), 400

    resultados = buscar_processo(entrada)
    if resultados:
        return jsonify(resultados)
    else:
        return jsonify({"erro": "Nenhum processo encontrado para o número informado"}), 404

@app.route("/")
def index():
    """Serve o arquivo index.html"""
    return send_from_directory(BASE_DIR, "index.html")

if __name__ == "__main__":
    app.run(debug=True)


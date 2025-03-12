import os
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Corrigindo caminho do banco de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Diretório onde está rodando
DB_PATH = os.path.join(BASE_DIR, "processos.db")  # Caminho correto para ambiente de produção

# Função para buscar processo no banco de dados
def buscar_processo(numero_processo):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT processo, vara, nome, status FROM processos WHERE processo = ?", (numero_processo,))
    resultado = cursor.fetchall()
    conn.close()

    if resultado:
        return [{"processo": r[0], "vara": r[1], "nome": r[2], "status": r[3]} for r in resultado]
    else:
        return []

@app.route("/consulta", methods=["GET"])
def consulta():
    numero_processo = request.args.get("processo")
    if not numero_processo:
        return jsonify({"erro": "Número do processo é obrigatório"}), 400

    resultados = buscar_processo(numero_processo)
    if resultados:
        return jsonify(resultados)
    else:
        return jsonify({"erro": "Processo não encontrado"}), 404


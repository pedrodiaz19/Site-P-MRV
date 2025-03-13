import os
import sqlite3
import re  # Biblioteca para manipulação de strings
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "processos.db")
CALCULOS_DIR = os.path.join(BASE_DIR, "calculos")  # Pasta onde os PDFs estão armazenados

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

def buscar_arquivo_calculo(nome):
    """Busca um arquivo de PDF na pasta 'calculos' baseado no nome."""
    nome_formatado = re.sub(r'[^a-zA-Z0-9]', '_', nome)  # Formata nome para evitar problemas com caracteres especiais
    for arquivo in os.listdir(CALCULOS_DIR):
        if arquivo.lower().startswith(nome_formatado.lower()) and arquivo.lower().endswith(".pdf"):
            return arquivo
    return None

@app.route("/consulta", methods=["GET"])
def consulta():
    entrada = request.args.get("processo")
    if not entrada:
        return jsonify({"erro": "Número do processo ou CPF é obrigatório"}), 400

    resultados = buscar_processo(entrada)
    if resultados:
        for resultado in resultados:
            nome = resultado["nome"]
            arquivo_pdf = buscar_arquivo_calculo(nome)
            if arquivo_pdf:
                resultado["arquivo_calculo"] = f"/calculos/{arquivo_pdf}"
        return jsonify(resultados)
    else:
        return jsonify({"erro": "Nenhum processo encontrado para o número informado"}), 404

@app.route("/calculos/<path:filename>")
def download_calculo(filename):
    """Serve os arquivos PDF da pasta 'calculos'."""
    return send_from_directory(CALCULOS_DIR, filename)

@app.route("/")
def index():
    """Serve o arquivo index.html"""
    return send_from_directory(BASE_DIR, "index.html")

if __name__ == "__main__":
    app.run(debug=True)


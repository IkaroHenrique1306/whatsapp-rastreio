# ============================================================
# Sistema de Rastreamento de Encomendas via WhatsApp
# Desenvolvido por:
#   Íkaro Henrique Marçal Alexandre
#   Matheus Kioshi Fernandes Numata
#
# © 2025 - Todos os direitos reservados.
# Este software é propriedade intelectual dos autores.
# A reprodução, modificação ou distribuição não autorizada
# é estritamente proibida.
# ============================================================

from flask import Flask, render_template, request, redirect, jsonify
import json
import os

app = Flask(__name__)

DADOS_FILE = "dados.json"

def carregar_dados():
    if not os.path.exists(DADOS_FILE):
        return {}
    with open(DADOS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_dados(dados):
    with open(DADOS_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

@app.route("/")
def index():
    dados = carregar_dados()
    return render_template("index.html", dados=dados)

@app.route("/adicionar", methods=["POST"])
def adicionar():
    nome = request.form.get("nome").strip()
    numero = request.form.get("numero").strip()
    codigo = request.form.get("codigo").strip()
    if nome and numero and codigo:
        dados = carregar_dados()
        if nome not in dados:
            dados[nome] = {}
        dados[nome][numero] = codigo
        salvar_dados(dados)
    return redirect("/")

@app.route("/remover/<nome>/<numero>")
def remover(nome, numero):
    dados = carregar_dados()
    if nome in dados and numero in dados[nome]:
        del dados[nome][numero]
        if not dados[nome]:
            del dados[nome]
        salvar_dados(dados)
    return redirect("/")

@app.route("/dados")
def dados():
    return jsonify(carregar_dados())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

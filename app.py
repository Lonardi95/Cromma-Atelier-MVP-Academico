"""Interface HTTP mínima do MVP acadêmico; sem autenticação, ainda em desenvolvimento."""
from flask import Flask, jsonify, request
from database import connect, initialize
from inventory import EstoqueInvalido, movimentar

app = Flask(__name__)

@app.get("/")
def inicio():
    return jsonify(sistema="CROMMA ATELIER SYSTEM - MVP acadêmico", estado="em desenvolvimento")

@app.get("/produtos")
def produtos():
    with connect() as con:
        return jsonify([dict(r) for r in con.execute("SELECT id,nome,sku,tipo,estoque_atual FROM produtos ORDER BY id")])

@app.post("/movimentacoes")
def registrar():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(erro="Envie um objeto JSON."), 400
    try:
        saldo = movimentar(data.get("produto_id"), data.get("tipo"), data.get("quantidade"))
    except EstoqueInvalido as exc:
        return jsonify(erro=str(exc)), 400
    return jsonify(mensagem="Movimentação registrada.", saldo_atual=saldo), 201

if __name__ == "__main__":
    initialize()
    app.run(debug=False)

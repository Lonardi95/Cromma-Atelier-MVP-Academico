"""Aplicação demonstrativa CROMMA ATELIER SYSTEM — dados exclusivamente fictícios."""
import os
from flask import Flask, jsonify, redirect, render_template, request, url_for
from database import connect, initialize
from inventory import EstoqueInvalido, movimentar

app = Flask(__name__)


def garantir_dados_demo():
    """Inicializa as tabelas e adiciona somente itens de demonstração."""
    initialize()
    with connect() as con:
        con.execute(
            "INSERT OR IGNORE INTO produtos(nome,sku,tipo,estoque_atual) VALUES(?,?,?,?)",
            ("Quadro Decorativo Abstrato 90 × 60 cm", "DEMO-QD001", "produto", 15),
        )
        con.execute(
            "INSERT OR IGNORE INTO produtos(nome,sku,tipo,estoque_atual) VALUES(?,?,?,?)",
            ("Moldura preta 60 × 40 cm", "DEMO-MAT001", "material", 8),
        )


@app.get("/health")
def health():
    """Monitoramento basico de disponibilidade e acesso ao banco demonstrativo."""
    try:
        garantir_dados_demo()
        with connect() as con:
            con.execute("SELECT 1").fetchone()
        return jsonify(status="ok", servico="cromma-mvp-academico"), 200
    except Exception:
        app.logger.exception("Falha na verificacao de saude")
        return jsonify(status="erro"), 503


@app.get("/")
@app.get("/painel")
def inicio():
    return _render_pagina("inicio")


@app.get("/estoque")
def pagina_produtos():
    return _render_pagina("produtos")


@app.get("/nova-movimentacao")
def pagina_movimentacao():
    return _render_pagina("movimentacao")


def _render_pagina(pagina):
    garantir_dados_demo()
    with connect() as con:
        produtos_lista = [
            dict(linha) for linha in con.execute(
                "SELECT id,nome,sku,tipo,estoque_atual FROM produtos ORDER BY id"
            )
        ]
        movimentacoes = con.execute(
            "SELECT COUNT(*) FROM movimentacoes"
        ).fetchone()[0]
    estado = request.args.get("estado")
    if estado == "ok":
        acao = "Entrada" if request.args.get("acao") == "entrada" else "Saída"
        saldo = request.args.get("saldo", "")
        alerta = f"{acao} registrada com sucesso! Novo saldo: {saldo} unidade(s)."
        classe = "success"
    elif estado == "erro":
        alerta = request.args.get("mensagem", "Não foi possível realizar a operação.")[:180]
        classe = "error"
    else:
        alerta, classe = None, ""
    return render_template(
        "index.html",
        pagina=pagina,
        produtos=produtos_lista,
        unidades=sum(produto["estoque_atual"] for produto in produtos_lista),
        movimentacoes=movimentacoes,
        alerta=alerta,
        alerta_classe=classe,
        ambiente_temporario=bool(os.getenv("VERCEL")),
    )


@app.post("/interface/movimentar")
def movimentar_interface():
    garantir_dados_demo()
    quantidade_texto = request.form.get("quantidade", "").strip()
    try:
        quantidade = int(quantidade_texto) if quantidade_texto.isdecimal() else None
        produto_id_texto = request.form.get("produto_id", "").strip()
        produto_id = int(produto_id_texto) if produto_id_texto.isdecimal() else None
        tipo = request.form.get("tipo", "")
        saldo = movimentar(produto_id, tipo, quantidade)
    except EstoqueInvalido as erro:
        return redirect(url_for("pagina_movimentacao", estado="erro", mensagem=str(erro)))
    return redirect(url_for("pagina_movimentacao", estado="ok", acao=tipo, saldo=saldo))


@app.get("/produtos")
def produtos():
    with connect() as con:
        return jsonify([
            dict(linha) for linha in con.execute(
                "SELECT id,nome,sku,tipo,estoque_atual FROM produtos ORDER BY id"
            )
        ])


@app.post("/movimentacoes")
def registrar():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(erro="Envie um objeto JSON."), 400
    try:
        saldo = movimentar(data.get("produto_id"), data.get("tipo"), data.get("quantidade"))
    except EstoqueInvalido as erro:
        return jsonify(erro=str(erro)), 400
    return jsonify(mensagem="Movimentação registrada.", saldo_atual=saldo), 201


if __name__ == "__main__":
    initialize()
    app.run(debug=False)

"""Regras de movimentação de estoque com transação atômica."""
from database import connect

class EstoqueInvalido(ValueError):
    pass

def movimentar(produto_id, tipo, quantidade, path=None):
    if tipo not in ("entrada", "saida") or type(quantidade) is not int or quantidade <= 0:
        raise EstoqueInvalido("Informe tipo válido e quantidade inteira positiva.")
    if type(produto_id) is not int or produto_id <= 0:
        raise EstoqueInvalido("Produto inválido.")
    con = connect(path) if path is not None else connect()
    try:
        con.execute("BEGIN IMMEDIATE")
        item = con.execute("SELECT estoque_atual FROM produtos WHERE id=?", (produto_id,)).fetchone()
        if item is None:
            raise EstoqueInvalido("Produto não encontrado.")
        saldo = item["estoque_atual"] + (quantidade if tipo == "entrada" else -quantidade)
        if saldo < 0:
            raise EstoqueInvalido("Saldo insuficiente.")
        con.execute("UPDATE produtos SET estoque_atual=? WHERE id=?", (saldo, produto_id))
        con.execute("INSERT INTO movimentacoes(produto_id,tipo,quantidade) VALUES(?,?,?)", (produto_id,tipo,quantidade))
        con.commit()
        return saldo
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()

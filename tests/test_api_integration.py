"""Integração entre a API Flask, o serviço de estoque e o SQLite."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from database import connect, initialize
import app as webapp

class ApiIntegracaoTestes(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "integracao.sqlite3"
        initialize(self.path)
        with connect(self.path) as con:
            con.execute("INSERT INTO produtos(nome,sku,tipo,estoque_atual) VALUES(?,?,?,?)", ("Quadro demonstrativo","DEMO-API-01","produto",15))
        self.client = webapp.app.test_client()
        self.patch_db = patch.object(webapp, "connect", side_effect=lambda: connect(self.path))
        self.patch_move = patch.object(webapp, "movimentar", side_effect=self.movimentar_teste)
        self.patch_db.start()
        self.patch_move.start()

    def movimentar_teste(self, produto_id, tipo, quantidade):
        from inventory import movimentar
        return movimentar(produto_id, tipo, quantidade, self.path)

    def tearDown(self):
        self.patch_move.stop()
        self.patch_db.stop()
        self.tmp.cleanup()

    def test_consulta_produtos(self):
        response = self.client.get("/produtos")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()[0]["sku"], "DEMO-API-01")

    def test_saida_por_http_persiste_no_banco(self):
        response = self.client.post("/movimentacoes", json={"produto_id":1,"tipo":"saida","quantidade":3})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["saldo_atual"], 12)
        with connect(self.path) as con:
            self.assertEqual(con.execute("SELECT estoque_atual FROM produtos WHERE id=1").fetchone()[0], 12)

    def test_json_invalido_rejeitado(self):
        response = self.client.post("/movimentacoes", data="não é json", content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_saldo_insuficiente_por_http(self):
        response = self.client.post("/movimentacoes", json={"produto_id":1,"tipo":"saida","quantidade":99})
        self.assertEqual(response.status_code, 400)
        with connect(self.path) as con:
            self.assertEqual(con.execute("SELECT estoque_atual FROM produtos WHERE id=1").fetchone()[0], 15)

if __name__ == "__main__":
    unittest.main()

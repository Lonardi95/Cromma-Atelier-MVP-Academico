"""Testes unitários da regra central de estoque."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from database import initialize, connect
from inventory import EstoqueInvalido, movimentar

class EstoqueTestes(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "teste.sqlite3"
        initialize(self.path)
        with connect(self.path) as con:
            con.execute("INSERT INTO produtos(nome,sku,tipo,estoque_atual) VALUES(?,?,?,?)", ("Quadro fictício","DEMO-001","produto",15))

    def tearDown(self):
        self.temp.cleanup()

    def test_saida_valida(self):
        self.assertEqual(movimentar(1,"saida",3,self.path),12)
        with connect(self.path) as con:
            self.assertEqual(con.execute("SELECT COUNT(*) FROM movimentacoes").fetchone()[0],1)

    def test_saldo_insuficiente_nao_altera_estoque(self):
        with self.assertRaises(EstoqueInvalido):
            movimentar(1,"saida",20,self.path)
        with connect(self.path) as con:
            self.assertEqual(con.execute("SELECT estoque_atual FROM produtos WHERE id=1").fetchone()[0],15)
            self.assertEqual(con.execute("SELECT COUNT(*) FROM movimentacoes").fetchone()[0],0)

    def test_quantidade_invalida(self):
        for quantidade in (0,-1,1.5,True,"3"):
            with self.assertRaises(EstoqueInvalido):
                movimentar(1,"entrada",quantidade,self.path)

if __name__ == "__main__":
    unittest.main()

"""Testes adicionais de consistência e rastreabilidade de estoque."""
import tempfile
import unittest
from pathlib import Path
from database import connect, initialize
from inventory import EstoqueInvalido, movimentar

class RevisaoEstoqueTestes(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "test.sqlite3"
        initialize(self.db)
        with connect(self.db) as con:
            con.execute("INSERT INTO produtos(nome,sku,tipo,estoque_atual) VALUES(?,?,?,?)", ("Material demonstrativo", "DEMO-MAT-01", "material", 5))

    def tearDown(self):
        self.tmp.cleanup()

    def test_entrada_atualiza_saldo_e_historico(self):
        self.assertEqual(movimentar(1, "entrada", 4, self.db), 9)
        with connect(self.db) as con:
            movimento = con.execute("SELECT tipo,quantidade FROM movimentacoes").fetchone()
            self.assertEqual(tuple(movimento), ("entrada", 4))

    def test_produto_inexistente_nao_gera_movimento(self):
        with self.assertRaises(EstoqueInvalido):
            movimentar(999, "saida", 1, self.db)
        with connect(self.db) as con:
            self.assertEqual(con.execute("SELECT COUNT(*) FROM movimentacoes").fetchone()[0], 0)

    def test_tipo_invalido_nao_altera_saldo(self):
        with self.assertRaises(EstoqueInvalido):
            movimentar(1, "ajuste", 1, self.db)
        with connect(self.db) as con:
            self.assertEqual(con.execute("SELECT estoque_atual FROM produtos WHERE id=1").fetchone()[0], 5)

if __name__ == "__main__":
    unittest.main()

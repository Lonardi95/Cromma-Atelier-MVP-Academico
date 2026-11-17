"""Persistência SQLite do MVP acadêmico, sem dados reais."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("mvp.sqlite3")

SCHEMA = """
CREATE TABLE IF NOT EXISTS produtos (
 id INTEGER PRIMARY KEY,
 nome TEXT NOT NULL,
 sku TEXT NOT NULL UNIQUE,
 tipo TEXT NOT NULL CHECK(tipo IN ('produto','material')),
 estoque_atual INTEGER NOT NULL DEFAULT 0 CHECK(estoque_atual >= 0)
);
CREATE TABLE IF NOT EXISTS movimentacoes (
 id INTEGER PRIMARY KEY,
 produto_id INTEGER NOT NULL REFERENCES produtos(id),
 tipo TEXT NOT NULL CHECK(tipo IN ('entrada','saida')),
 quantidade INTEGER NOT NULL CHECK(quantidade > 0),
 criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

def connect(path=DB_PATH):
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con

def initialize(path=DB_PATH):
    with connect(path) as con:
        con.executescript(SCHEMA)

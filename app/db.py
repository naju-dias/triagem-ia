import sqlite3
from .schemas import Triagem

DB = "triagem.db"

def conectar():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def criar_tabela():
    with conectar() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS triagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            mensagem TEXT, categoria TEXT, urgencia TEXT, confianca REAL,
            resumo TEXT, nome TEXT, valor_solicitado REAL,
            tipo_negocio TEXT, resposta_sugerida TEXT,
            revisao_humana INTEGER DEFAULT 0
        )""")

def salvar(mensagem: str, t: Triagem, revisao: bool) -> int:
    with conectar() as con:
        cur = con.execute(
            """INSERT INTO triagens (mensagem, categoria, urgencia, confianca, resumo,
               nome, valor_solicitado, tipo_negocio, resposta_sugerida, revisao_humana)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (mensagem, t.categoria, t.urgencia, t.confianca, t.resumo, t.nome,
             t.valor_solicitado, t.tipo_negocio, t.resposta_sugerida, int(revisao)),
        )
        return cur.lastrowid

def listar(limite: int = 50):
    with conectar() as con:
        return [dict(r) for r in con.execute(
            "SELECT * FROM triagens ORDER BY id DESC LIMIT ?", (limite,))]
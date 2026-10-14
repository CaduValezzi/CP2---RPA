"""Histórico em SQLite para só notificar vagas novas."""
import sqlite3
from contextlib import closing

from config import DB_PATH
from scraper import Vaga


def _conectar() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.execute(
        "CREATE TABLE IF NOT EXISTS vagas ("
        "id TEXT PRIMARY KEY, titulo TEXT, empresa TEXT, url TEXT, "
        "visto_em TEXT DEFAULT CURRENT_TIMESTAMP)"
    )
    return con


def filtrar_novas(vagas: list[Vaga]) -> list[Vaga]:
    with closing(_conectar()) as con:
        ja_vistas = {linha[0] for linha in con.execute("SELECT id FROM vagas")}
    return [v for v in vagas if v.id not in ja_vistas]


def registrar(vagas: list[Vaga]) -> None:
    with closing(_conectar()) as con, con:
        con.executemany(
            "INSERT OR IGNORE INTO vagas (id, titulo, empresa, url) VALUES (?, ?, ?, ?)",
            [(v.id, v.titulo, v.empresa, v.url) for v in vagas],
        )

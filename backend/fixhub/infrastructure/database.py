from contextlib import contextmanager
from pathlib import Path
import sqlite3
from typing import Iterator


class Database:
    """Gerencia conexões, transações e criação do esquema SQLite."""

    def __init__(self, caminho: str | Path):
        self._caminho = str(caminho)
        if self._caminho != ":memory:":
            Path(self._caminho).parent.mkdir(parents=True, exist_ok=True)

    @property
    def caminho(self) -> str:
        return self._caminho

    @contextmanager
    def transacao(self) -> Iterator[sqlite3.Connection]:
        conexao = sqlite3.connect(self._caminho, timeout=5)
        try:
            conexao.row_factory = sqlite3.Row
            conexao.execute("PRAGMA foreign_keys = ON")
            conexao.execute("PRAGMA busy_timeout = 5000")
            yield conexao
            conexao.commit()
        except Exception:
            conexao.rollback()
            raise
        finally:
            conexao.close()

    def inicializar(self) -> None:
        comandos = (
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL COLLATE NOCASE UNIQUE,
                senha_hash TEXT NOT NULL,
                perfil TEXT NOT NULL
                    CHECK (perfil IN ('morador', 'administrador'))
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS chamados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descricao TEXT NOT NULL,
                localizacao TEXT NOT NULL,
                estado TEXT NOT NULL DEFAULT 'Aberto'
                    CHECK (estado IN ('Aberto', 'Em Análise', 'Resolvido')),
                morador_id INTEGER NOT NULL,
                FOREIGN KEY (morador_id) REFERENCES usuarios(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS historico_estados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chamado_id INTEGER NOT NULL,
                estado_anterior TEXT NOT NULL,
                estado_novo TEXT NOT NULL,
                administrador_id INTEGER NOT NULL,
                data_hora TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chamado_id) REFERENCES chamados(id),
                FOREIGN KEY (administrador_id) REFERENCES usuarios(id)
            )
            """,
            "CREATE INDEX IF NOT EXISTS idx_chamados_morador "
            "ON chamados (morador_id, id DESC)",
            "CREATE INDEX IF NOT EXISTS idx_chamados_estado "
            "ON chamados (estado, id DESC)",
            "CREATE INDEX IF NOT EXISTS idx_historico_chamado "
            "ON historico_estados (chamado_id, id)",
        )
        with self.transacao() as conexao:
            for comando in comandos:
                conexao.execute(comando)

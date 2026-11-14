import sqlite3
from pathlib import Path


CAMINHO_BANCO = Path(__file__).resolve().with_name("fixhub.db")


def conectar_banco() -> sqlite3.Connection:
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def inicializar_banco() -> None:
    conexao = conectar_banco()
    try:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL COLLATE NOCASE UNIQUE,
                senha_hash TEXT NOT NULL,
                perfil TEXT NOT NULL
                    CHECK (perfil IN ('morador', 'administrador'))
            )
            """
        )

        conexao.execute(
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
            """
        )

        conexao.execute(
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
            """
        )

        conexao.commit()
    finally:
        conexao.close()


import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from flask import Flask, g, jsonify

import permissoes
from permissoes import requer_login, requer_perfil


class TestControleDeAcesso(unittest.TestCase):
    def setUp(self):
        self.diretorio_temporario = tempfile.TemporaryDirectory()
        self.caminho_banco = Path(self.diretorio_temporario.name) / "teste.db"
        self._criar_banco_de_teste()

        self.patch_conexao = patch(
            "permissoes.conectar_banco", self._conectar_banco_de_teste
        )
        self.patch_conexao.start()
        self.addCleanup(self.patch_conexao.stop)
        self.addCleanup(self.diretorio_temporario.cleanup)

        app = Flask(__name__)
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "chave-apenas-para-testes"

        @app.get("/privada")
        @requer_login
        def rota_privada():
            return jsonify({"usuario_id": g.usuario_atual["id"]})

        @app.get("/admin")
        @requer_perfil("administrador")
        def rota_administrativa():
            return jsonify({"mensagem": "acesso autorizado"})

        self.cliente = app.test_client()

    def _criar_banco_de_teste(self):
        conexao = sqlite3.connect(self.caminho_banco)
        try:
            conexao.execute(
                """
                CREATE TABLE usuarios (
                    id INTEGER PRIMARY KEY,
                    nome TEXT NOT NULL,
                    email TEXT NOT NULL,
                    senha_hash TEXT NOT NULL,
                    perfil TEXT NOT NULL
                        CHECK (perfil IN ('morador', 'administrador'))
                )
                """
            )
            conexao.executemany(
                """
                INSERT INTO usuarios (id, nome, email, senha_hash, perfil)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (1, "Morador de teste", "morador@example.com", "hash", "morador"),
                    (
                        2,
                        "Administrador de teste",
                        "admin@example.com",
                        "hash",
                        "administrador",
                    ),
                ],
            )
            conexao.commit()
        finally:
            conexao.close()

    def _conectar_banco_de_teste(self):
        conexao = sqlite3.connect(self.caminho_banco)
        conexao.row_factory = sqlite3.Row
        return conexao

    def _iniciar_sessao(self, usuario_id):
        with self.cliente.session_transaction() as sessao:
            sessao["usuario_id"] = usuario_id

    def test_rota_protegida_rejeita_usuario_sem_login(self):
        resposta = self.cliente.get("/privada")

        self.assertEqual(resposta.status_code, 401)
        self.assertEqual(resposta.get_json(), {"erro": "É necessário fazer login."})

    def test_rota_de_administrador_rejeita_morador(self):
        self._iniciar_sessao(1)

        resposta = self.cliente.get("/admin")

        self.assertEqual(resposta.status_code, 403)

    def test_rota_de_administrador_permite_administrador(self):
        self._iniciar_sessao(2)

        resposta = self.cliente.get("/admin")

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.get_json(), {"mensagem": "acesso autorizado"})

    def test_sessao_de_usuario_que_nao_existe_e_rejeitada(self):
        self._iniciar_sessao(999)

        resposta = self.cliente.get("/privada")

        self.assertEqual(resposta.status_code, 401)


if __name__ == "__main__":
    unittest.main()

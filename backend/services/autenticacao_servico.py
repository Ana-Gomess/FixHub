import re
import sqlite3

from domain.administrador import Administrador
from domain.errors import (
    CredenciaisInvalidas,
    DadosInvalidos,
    EmailDuplicado,
)
from domain.morador import Morador
from domain.usuario import Usuario
from repositories.usuario_repositorio import UsuarioRepositorio


FORMATO_EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


class AutenticacaoServico:


    def __init__(self, usuarios: UsuarioRepositorio):
        self._usuarios = usuarios

    @staticmethod
    def _normalizar_cadastro(
        nome: str | None, email: str | None, senha: str | None
    ) -> tuple[str, str, str]:
        if not all(isinstance(valor, str) for valor in (nome, email, senha)):
            raise DadosInvalidos("Nome, e-mail e senha devem ser textos.")

        nome = nome.strip()
        email = email.strip().lower()
        if not nome or not email or not senha.strip():
            raise DadosInvalidos("Nome, e-mail e senha são obrigatórios.")
        if not FORMATO_EMAIL.fullmatch(email):
            raise DadosInvalidos("Informe um e-mail válido.")
        return nome, email, senha

    def cadastrar_morador(
        self, nome: str | None, email: str | None, senha: str | None
    ) -> Usuario:
        nome, email, senha = self._normalizar_cadastro(nome, email, senha)
        morador = Morador.criar_com_senha(nome=nome, email=email, senha=senha)
        try:
            usuario = self._usuarios.salvar(morador)
        except sqlite3.IntegrityError as erro:
            raise EmailDuplicado("Este e-mail já está cadastrado.") from erro
        return usuario

    def autenticar(self, email: str | None, senha: str | None) -> Usuario:
        if not isinstance(email, str) or not isinstance(senha, str):
            raise DadosInvalidos("E-mail e senha devem ser textos.")
        email = email.strip().lower()
        if not email or not senha.strip():
            raise DadosInvalidos("E-mail e senha são obrigatórios.")

        usuario = self._usuarios.buscar_por_email(email)
        if usuario is None or not usuario.verificar_senha(senha):
            raise CredenciaisInvalidas("E-mail ou senha incorretos.")
        return usuario

    def buscar_usuario(self, usuario_id: int) -> Usuario | None:

        return self._usuarios.buscar_por_id(usuario_id)

    def criar_administrador(
        self, nome: str | None, email: str | None, senha: str | None
    ) -> Usuario:

        nome, email, senha = self._normalizar_cadastro(nome, email, senha)
        administrador = Administrador.criar_com_senha(
            nome=nome, email=email, senha=senha
        )
        try:
            usuario = self._usuarios.salvar(administrador)
        except sqlite3.IntegrityError as erro:
            raise EmailDuplicado("Este e-mail já está cadastrado.") from erro
        return usuario

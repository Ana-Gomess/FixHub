from domain.morador import Morador
from domain.usuario import Usuario
from domain.usuario_factory import UsuarioFactory
from infrastructure.database import Database
from repositories.base import usar_conexao


class UsuarioRepositorio:

    def __init__(self, banco: Database):
        self._banco = banco

    def salvar(self, usuario: Usuario) -> Usuario:
        bloco = usuario.bloco if isinstance(usuario, Morador) else None
        with usar_conexao(self._banco) as conexao:
            cursor = conexao.execute(
                """
                INSERT INTO usuarios (nome, email, senha_hash, perfil, bloco)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    usuario.nome,
                    usuario.email,
                    usuario._hash_para_persistencia(),
                    usuario.perfil,
                    bloco,
                ),
            )
            registro = conexao.execute(
                """
                SELECT id, nome, email, senha_hash, perfil, bloco
                FROM usuarios WHERE id = ?
                """,
                (cursor.lastrowid,),
            ).fetchone()
        return UsuarioFactory.a_partir_de(registro)

    def buscar_por_id(self, usuario_id: int) -> Usuario | None:
        if not isinstance(usuario_id, int) or usuario_id < 1:
            return None
        with usar_conexao(self._banco) as conexao:
            registro = conexao.execute(
                """
                SELECT id, nome, email, senha_hash, perfil, bloco
                FROM usuarios WHERE id = ?
                """,
                (usuario_id,),
            ).fetchone()
        return UsuarioFactory.a_partir_de(registro) if registro else None

    def buscar_por_email(self, email: str) -> Usuario | None:
        with usar_conexao(self._banco) as conexao:
            registro = conexao.execute(
                """
                SELECT id, nome, email, senha_hash, perfil, bloco
                FROM usuarios WHERE email = ?
                """,
                (email.strip().lower(),),
            ).fetchone()
        return UsuarioFactory.a_partir_de(registro) if registro else None

    def listar_moradores(self) -> list[dict[str, int | str | None]]:
        with usar_conexao(self._banco) as conexao:
            registros = conexao.execute(
                """
                SELECT id, nome, bloco FROM usuarios
                WHERE perfil = 'morador'
                ORDER BY nome COLLATE NOCASE
                """
            ).fetchall()
        return [dict(registro) for registro in registros]

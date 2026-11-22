from collections.abc import Mapping
from typing import Any

from fixhub.domain.administrador import Administrador
from fixhub.domain.errors import DadosInvalidos
from fixhub.domain.morador import Morador
from fixhub.domain.usuario import Usuario


class UsuarioFactory:
    """Reconstrói a classe de usuário correspondente ao perfil persistido."""

    @staticmethod
    def a_partir_de(registro: Mapping[str, Any]) -> Usuario:
        dados = dict(registro)
        tipo = {"morador": Morador, "administrador": Administrador}.get(
            dados.get("perfil")
        )
        if tipo is None:
            raise DadosInvalidos("O perfil salvo para o usuário é inválido.")
        return tipo(
            id=dados.get("id"),
            nome=dados["nome"],
            email=dados["email"],
            senha_hash=dados["senha_hash"],
        )

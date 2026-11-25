from collections.abc import Mapping
from typing import Any

from domain.administrador import Administrador
from domain.errors import DadosInvalidos
from domain.morador import Morador
from domain.usuario import Usuario


class UsuarioFactory:


    @staticmethod
    def a_partir_de(registro: Mapping[str, Any]) -> Usuario:
        dados = dict(registro)
        tipo = {"morador": Morador, "administrador": Administrador}.get(
            dados.get("perfil")
        )
        if tipo is None:
            raise DadosInvalidos("O perfil salvo para o usuário é inválido.")
        argumentos = {
            "id": dados.get("id"),
            "nome": dados["nome"],
            "email": dados["email"],
            "senha_hash": dados["senha_hash"],
        }
        if tipo is Morador:
            argumentos["bloco"] = dados.get("bloco")
        return tipo(**argumentos)

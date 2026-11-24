from __future__ import annotations

from abc import ABC, abstractmethod

from werkzeug.security import check_password_hash, generate_password_hash

from domain.errors import DadosInvalidos
from domain.permissions import Permissao


class Usuario(ABC):


    def __init__(self, *, id: int | None, nome: str, email: str, senha_hash: str):
        if not isinstance(nome, str) or not nome.strip():
            raise DadosInvalidos("O nome é obrigatório.")
        if not isinstance(email, str) or not email.strip():
            raise DadosInvalidos("O e-mail é obrigatório.")
        if not isinstance(senha_hash, str) or not senha_hash:
            raise DadosInvalidos("A senha precisa estar protegida por hash.")
        if id is not None and (not isinstance(id, int) or id < 1):
            raise DadosInvalidos("O id do usuário deve ser um inteiro positivo.")

        self._id = id
        self._nome = nome.strip()
        self._email = email.strip().lower()
        self.__senha_hash = senha_hash

    @property
    def id(self) -> int | None:
        return self._id

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def email(self) -> str:
        return self._email

    @property
    @abstractmethod
    def perfil(self) -> str:
        pass

    @abstractmethod
    def tem_permissao(self, permissao: Permissao) -> bool:
        pass

    @classmethod
    def criar_com_senha(
        cls,
        *,
        nome: str,
        email: str,
        senha: str,
        id: int | None = None,
    ) -> Usuario:
        if not isinstance(senha, str) or not senha.strip():
            raise DadosInvalidos("A senha é obrigatória.")
        return cls(
            id=id,
            nome=nome,
            email=email,
            senha_hash=generate_password_hash(senha),
        )

    def verificar_senha(self, senha: str) -> bool:
        return isinstance(senha, str) and check_password_hash(self.__senha_hash, senha)

    def _hash_para_persistencia(self) -> str:

        return self.__senha_hash

    def para_publico(self) -> dict[str, int | str | None]:

        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "perfil": self.perfil,
        }

from __future__ import annotations

from werkzeug.security import generate_password_hash

from domain.errors import DadosInvalidos
from domain.permissions import Permissao
from domain.usuario import Usuario


BLOCOS_DISPONIVEIS = ("A", "B", "C", "D", "E", "F")
BLOCOS_VALIDOS = frozenset(BLOCOS_DISPONIVEIS)


class Morador(Usuario):
    def __init__(
        self,
        *,
        id: int | None,
        nome: str,
        email: str,
        senha_hash: str,
        bloco: str | None = None,
    ):
        super().__init__(id=id, nome=nome, email=email, senha_hash=senha_hash)
        if bloco is not None:
            if not isinstance(bloco, str) or bloco.strip().upper() not in BLOCOS_VALIDOS:
                raise DadosInvalidos("O bloco deve ser uma letra de A a F.")
            bloco = bloco.strip().upper()
        self._bloco = bloco

    @property
    def bloco(self) -> str | None:
        return self._bloco

    @property
    def perfil(self) -> str:
        return "morador"

    def tem_permissao(self, permissao: Permissao) -> bool:
        return permissao in {
            Permissao.CRIAR_CHAMADO,
            Permissao.LISTAR_PROPRIOS_CHAMADOS,
        }

    @classmethod
    def criar_com_senha(
        cls,
        *,
        nome: str,
        email: str,
        senha: str,
        bloco: str | None = None,
        id: int | None = None,
    ) -> Morador:
        if not isinstance(senha, str) or not senha.strip():
            raise DadosInvalidos("A senha é obrigatória.")
        if not isinstance(bloco, str) or bloco.strip().upper() not in BLOCOS_VALIDOS:
            raise DadosInvalidos("Escolha um bloco entre A e F.")
        return cls(
            id=id,
            nome=nome,
            email=email,
            senha_hash=generate_password_hash(senha),
            bloco=bloco,
        )

    def para_publico(self) -> dict[str, int | str | None]:
        dados = super().para_publico()
        dados["bloco"] = self.bloco
        return dados

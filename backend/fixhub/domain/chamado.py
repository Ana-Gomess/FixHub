from __future__ import annotations

from fixhub.domain.administrador import Administrador
from fixhub.domain.errors import DadosInvalidos, SemPermissao, TransicaoInvalida
from fixhub.domain.estado_chamado import EstadoChamado
from fixhub.domain.historico_estado import HistoricoEstado
from fixhub.domain.permissions import Permissao


class Chamado:
    """Chamado de manutenção, com validação e regras de mudança de estado."""

    def __init__(
        self,
        *,
        id: int | None,
        titulo: str,
        descricao: str,
        localizacao: str,
        morador_id: int,
        estado: str | EstadoChamado = EstadoChamado.ABERTO,
        morador_nome: str | None = None,
    ):
        for campo, valor in (
            ("Título", titulo),
            ("Descrição", descricao),
            ("Localização", localizacao),
        ):
            if not isinstance(valor, str) or not valor.strip():
                raise DadosInvalidos(f"{campo} é obrigatório.")
        if not isinstance(morador_id, int) or morador_id < 1:
            raise DadosInvalidos("O chamado precisa estar vinculado a um morador.")
        if id is not None and (not isinstance(id, int) or id < 1):
            raise DadosInvalidos("O id do chamado deve ser um inteiro positivo.")

        self._id = id
        self._titulo = titulo.strip()
        self._descricao = descricao.strip()
        self._localizacao = localizacao.strip()
        self._morador_id = morador_id
        self._morador_nome = morador_nome
        self._estado = EstadoChamado.converter(estado)

    @property
    def id(self) -> int | None:
        return self._id

    @property
    def titulo(self) -> str:
        return self._titulo

    @property
    def descricao(self) -> str:
        return self._descricao

    @property
    def localizacao(self) -> str:
        return self._localizacao

    @property
    def morador_id(self) -> int:
        return self._morador_id

    @property
    def morador_nome(self) -> str | None:
        return self._morador_nome

    @property
    def estado(self) -> EstadoChamado:
        return self._estado

    def com_id(self, chamado_id: int) -> Chamado:
        """Retorna uma cópia do chamado com o id gerado pelo banco."""
        return Chamado(
            id=chamado_id,
            titulo=self.titulo,
            descricao=self.descricao,
            localizacao=self.localizacao,
            morador_id=self.morador_id,
            estado=self.estado,
            morador_nome=self.morador_nome,
        )

    def transicionar_para(
        self, novo_estado: str | EstadoChamado, administrador: Administrador
    ) -> HistoricoEstado:
        if not administrador.tem_permissao(Permissao.ALTERAR_ESTADO):
            raise SemPermissao("Somente um administrador pode alterar o estado.")
        if self.id is None or administrador.id is None:
            raise DadosInvalidos(
                "Salve o chamado e o administrador antes da alteração."
            )

        destino = EstadoChamado.converter(novo_estado)
        if destino not in self.estado.proximos_estados:
            raise TransicaoInvalida(
                f"Não é permitido alterar o estado de '{self.estado.value}' "
                f"para '{destino.value}'."
            )

        anterior = self._estado
        self._estado = destino
        return HistoricoEstado(
            chamado_id=self.id,
            estado_anterior=anterior,
            estado_novo=destino,
            administrador_id=administrador.id,
        )

    def para_publico(self, *, incluir_morador_id: bool = False) -> dict:
        dados = {
            "id": self.id,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "localizacao": self.localizacao,
            "estado": self.estado.value,
        }
        if incluir_morador_id:
            dados["morador_id"] = self.morador_id
        return dados

from __future__ import annotations

from enum import Enum

from fixhub.domain.errors import DadosInvalidos


class EstadoChamado(str, Enum):
    ABERTO = "Aberto"
    EM_ANALISE = "Em Análise"
    RESOLVIDO = "Resolvido"

    @classmethod
    def converter(cls, valor: str | EstadoChamado) -> EstadoChamado:
        if isinstance(valor, cls):
            return valor
        if isinstance(valor, str):
            valor = valor.strip()
        try:
            return cls(valor)
        except (TypeError, ValueError) as erro:
            raise DadosInvalidos(
                "Estado inválido. Use: Aberto, Em Análise ou Resolvido."
            ) from erro

    @property
    def proximos_estados(self) -> frozenset[EstadoChamado]:
        transicoes = {
            EstadoChamado.ABERTO: frozenset(
                {EstadoChamado.EM_ANALISE, EstadoChamado.RESOLVIDO}
            ),
            EstadoChamado.EM_ANALISE: frozenset({EstadoChamado.RESOLVIDO}),
            EstadoChamado.RESOLVIDO: frozenset(),
        }
        return transicoes[self]

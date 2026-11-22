from dataclasses import dataclass, field
from datetime import datetime, timezone

from fixhub.domain.estado_chamado import EstadoChamado


@dataclass(frozen=True)
class HistoricoEstado:
    """Registro imutável de uma transição executada por um administrador."""

    chamado_id: int
    estado_anterior: EstadoChamado
    estado_novo: EstadoChamado
    administrador_id: int
    data_hora: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def para_publico(self) -> dict[str, int | str]:
        return {
            "chamado_id": self.chamado_id,
            "estado_anterior": self.estado_anterior.value,
            "estado_novo": self.estado_novo.value,
            "administrador_id": self.administrador_id,
            "data_hora": self.data_hora.isoformat(),
        }

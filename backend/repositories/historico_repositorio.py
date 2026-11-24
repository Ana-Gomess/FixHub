from datetime import datetime
import sqlite3

from domain.estado_chamado import EstadoChamado
from domain.historico_estado import HistoricoEstado
from infrastructure.database import Database
from repositories.base import usar_conexao


class HistoricoRepositorio:


    def __init__(self, banco: Database):
        self._banco = banco



    def salvar(
        self,
        historico: HistoricoEstado,
        conexao: sqlite3.Connection | None = None,
    ) -> None:
        with usar_conexao(self._banco, conexao) as ativa:
            ativa.execute(
                """
                INSERT INTO historico_estados (
                    chamado_id, estado_anterior, estado_novo,
                    administrador_id, data_hora
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    historico.chamado_id,
                    historico.estado_anterior.value,
                    historico.estado_novo.value,
                    historico.administrador_id,
                    historico.data_hora.isoformat(),
                ),
            )

    def listar_por_chamado(self, chamado_id: int) -> list[HistoricoEstado]:
        with usar_conexao(self._banco) as conexao:
            registros = conexao.execute(
                """
                SELECT chamado_id, estado_anterior, estado_novo,
                       administrador_id, data_hora
                FROM historico_estados
                WHERE chamado_id = ?
                ORDER BY id ASC
                """,
                (chamado_id,),
            ).fetchall()
        return [
            HistoricoEstado(
                chamado_id=registro["chamado_id"],
                estado_anterior=EstadoChamado.converter(registro["estado_anterior"]),
                estado_novo=EstadoChamado.converter(registro["estado_novo"]),
                administrador_id=registro["administrador_id"],
                data_hora=datetime.fromisoformat(registro["data_hora"]),
            )
            for registro in registros
        ]

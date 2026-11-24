import sqlite3

from domain.chamado import Chamado
from domain.estado_chamado import EstadoChamado
from domain.errors import RecursoNaoEncontrado
from infrastructure.database import Database
from repositories.base import usar_conexao


class ChamadoRepositorio:


    def __init__(self, banco: Database):
        self._banco = banco

    @staticmethod
    def _modelo(registro: sqlite3.Row) -> Chamado:
        colunas = registro.keys()
        return Chamado(
            id=registro["id"],
            titulo=registro["titulo"],
            descricao=registro["descricao"],
            localizacao=registro["localizacao"],
            morador_id=registro["morador_id"],
            estado=registro["estado"],
            morador_nome=registro["morador_nome"] if "morador_nome" in colunas else None,
        )

    def salvar(self, chamado: Chamado) -> Chamado:
        with usar_conexao(self._banco) as conexao:
            cursor = conexao.execute(
                """
                INSERT INTO chamados (titulo, descricao, localizacao, estado, morador_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    chamado.titulo,
                    chamado.descricao,
                    chamado.localizacao,
                    chamado.estado.value,
                    chamado.morador_id,
                ),
            )
            chamado_id = cursor.lastrowid
        return chamado.com_id(chamado_id)

    def buscar_por_id(
        self, chamado_id: int, conexao: sqlite3.Connection | None = None
    ) -> Chamado | None:
        with usar_conexao(self._banco, conexao) as ativa:
            registro = ativa.execute(
                """
                SELECT id, titulo, descricao, localizacao, estado, morador_id
                FROM chamados WHERE id = ?
                """,
                (chamado_id,),
            ).fetchone()
        return self._modelo(registro) if registro else None

    def listar_por_morador(self, morador_id: int) -> list[Chamado]:
        with usar_conexao(self._banco) as conexao:
            registros = conexao.execute(
                """
                SELECT id, titulo, descricao, localizacao, estado, morador_id
                FROM chamados WHERE morador_id = ? ORDER BY id DESC
                """,
                (morador_id,),
            ).fetchall()
        return [self._modelo(registro) for registro in registros]

    def listar_todos(
        self,
        estado: EstadoChamado | None = None,
        morador_id: int | None = None,
    ) -> list[Chamado]:
        filtros = []
        parametros: list[object] = []
        if estado is not None:
            filtros.append("chamados.estado = ?")
            parametros.append(estado.value)
        if morador_id is not None:
            filtros.append("chamados.morador_id = ?")
            parametros.append(morador_id)

        consulta = """
            SELECT chamados.id, chamados.titulo, chamados.descricao,
                   chamados.localizacao, chamados.estado, chamados.morador_id,
                   usuarios.nome AS morador_nome
            FROM chamados
            JOIN usuarios ON usuarios.id = chamados.morador_id
        """
        if filtros:
            consulta += " WHERE " + " AND ".join(filtros)
        consulta += " ORDER BY chamados.id DESC"

        with usar_conexao(self._banco) as conexao:
            registros = conexao.execute(consulta, parametros).fetchall()
        return [self._modelo(registro) for registro in registros]

    def contar_por_estado(self) -> dict[str, int]:
        with usar_conexao(self._banco) as conexao:
            registro = conexao.execute(
                """
                SELECT
                    COUNT(CASE WHEN estado = 'Aberto' THEN 1 END) AS abertos,
                    COUNT(CASE WHEN estado = 'Em Análise' THEN 1 END) AS em_analise,
                    COUNT(CASE WHEN estado = 'Resolvido' THEN 1 END) AS resolvidos
                FROM chamados
                """
            ).fetchone()
        return dict(registro)



    def atualizar_estado(
        self, chamado: Chamado, conexao: sqlite3.Connection
    ) -> None:
        cursor = conexao.execute(
            "UPDATE chamados SET estado = ? WHERE id = ?",
            (chamado.estado.value, chamado.id),
        )
        if cursor.rowcount == 0:
            raise RecursoNaoEncontrado("Chamado não encontrado.")

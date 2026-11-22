from fixhub.domain.chamado import Chamado
from fixhub.domain.estado_chamado import EstadoChamado
from fixhub.domain.errors import (
    DadosInvalidos,
    RecursoNaoEncontrado,
    SemPermissao,
)
from fixhub.domain.permissions import Permissao
from fixhub.domain.usuario import Usuario
from fixhub.infrastructure.database import Database
from fixhub.repositories.chamado_repositorio import ChamadoRepositorio
from fixhub.repositories.historico_repositorio import HistoricoRepositorio


class ChamadoServico:
    """Casos de uso de chamados para moradores e administradores."""

    def __init__(
        self,
        banco: Database,
        chamados: ChamadoRepositorio,
        historicos: HistoricoRepositorio,
    ):
        self._banco = banco
        self._chamados = chamados
        self._historicos = historicos

    def criar(self, usuario: Usuario, dados: object) -> Chamado:
        if not usuario.tem_permissao(Permissao.CRIAR_CHAMADO):
            raise SemPermissao("Somente moradores podem abrir chamados.")
        if not isinstance(dados, dict):
            raise DadosInvalidos("Envie os dados do chamado em formato JSON.")
        if usuario.id is None:
            raise DadosInvalidos("Faça login novamente antes de abrir um chamado.")

        chamado = Chamado(
            id=None,
            titulo=dados.get("titulo"),
            descricao=dados.get("descricao"),
            localizacao=dados.get("localizacao"),
            morador_id=usuario.id,
        )
        return self._chamados.salvar(chamado)

    def listar_do_morador(self, usuario: Usuario) -> list[Chamado]:
        if not usuario.tem_permissao(Permissao.LISTAR_PROPRIOS_CHAMADOS):
            raise SemPermissao("Este perfil não pode listar chamados de morador.")
        if usuario.id is None:
            raise DadosInvalidos("Faça login novamente para listar chamados.")
        return self._chamados.listar_por_morador(usuario.id)

    def detalhes(self, usuario: Usuario, chamado_id: int) -> dict:
        if not isinstance(chamado_id, int) or chamado_id < 1:
            raise DadosInvalidos("O id do chamado deve ser positivo.")

        chamado = self._chamados.buscar_por_id(chamado_id)
        if chamado is None:
            raise RecursoNaoEncontrado("Chamado não encontrado.")

        pode_ver_todos = usuario.tem_permissao(Permissao.LISTAR_TODOS_CHAMADOS)
        pode_ver_proprio = (
            usuario.tem_permissao(Permissao.LISTAR_PROPRIOS_CHAMADOS)
            and chamado.morador_id == usuario.id
        )
        if not (pode_ver_todos or pode_ver_proprio):
            # Evita revelar que o chamado de outra pessoa existe.
            raise RecursoNaoEncontrado("Chamado não encontrado.")

        return {
            "chamado": chamado.para_publico(incluir_morador_id=pode_ver_todos),
            "historico": [
                item.para_publico()
                for item in self._historicos.listar_por_chamado(chamado_id)
            ],
        }

    def alterar_estado(
        self, administrador: Usuario, chamado_id: int, novo_estado: object
    ) -> Chamado:
        if not administrador.tem_permissao(Permissao.ALTERAR_ESTADO):
            raise SemPermissao("Somente um administrador pode alterar o estado.")
        if not isinstance(chamado_id, int) or chamado_id < 1:
            raise DadosInvalidos("O id do chamado deve ser positivo.")
        if not isinstance(novo_estado, str) or not novo_estado.strip():
            raise DadosInvalidos("O estado é obrigatório.")
        if administrador.id is None:
            raise DadosInvalidos("Salve o administrador antes de alterar o estado.")

        destino = EstadoChamado.converter(novo_estado)
        with self._banco.transacao() as conexao:
            chamado = self._chamados.buscar_por_id(chamado_id, conexao)
            if chamado is None:
                raise RecursoNaoEncontrado("Chamado não encontrado.")

            historico = chamado.transicionar_para(destino, administrador)
            self._chamados.atualizar_estado(chamado, conexao)
            self._historicos.salvar(historico, conexao)

        return chamado

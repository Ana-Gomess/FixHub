from domain.chamado import Chamado
from domain.estado_chamado import EstadoChamado
from domain.errors import DadosInvalidos, SemPermissao
from domain.permissions import Permissao
from domain.usuario import Usuario
from repositories.chamado_repositorio import ChamadoRepositorio


class PainelChamadosServico:


    def __init__(self, chamados: ChamadoRepositorio):
        self._chamados = chamados

    def listar(
        self,
        administrador: Usuario,
        *,
        estado: str | EstadoChamado | None = None,
        morador_id: str | int | None = None,
    ) -> list[Chamado]:
        if not administrador.tem_permissao(Permissao.LISTAR_TODOS_CHAMADOS):
            raise SemPermissao("Somente administradores podem listar todos os chamados.")

        estado_validado = EstadoChamado.converter(estado) if estado is not None else None
        morador_id_validado = self._validar_morador_id(morador_id)
        return self._chamados.listar_todos(estado_validado, morador_id_validado)

    def contar_por_estado(self, administrador: Usuario) -> dict[str, int]:
        if not administrador.tem_permissao(Permissao.VER_CONTAGENS):
            raise SemPermissao("Somente administradores podem consultar as contagens.")
        return self._chamados.contar_por_estado()

    @staticmethod
    def _validar_morador_id(valor: str | int | None) -> int | None:
        if valor is None:
            return None

        try:
            if isinstance(valor, bool) or not isinstance(valor, (str, int)):
                raise ValueError
            morador_id = int(valor)
        except (TypeError, ValueError) as erro:
            raise DadosInvalidos(
                "O parâmetro morador_id deve ser um inteiro positivo."
            ) from erro

        if morador_id < 1:
            raise DadosInvalidos(
                "O parâmetro morador_id deve ser um inteiro positivo."
            )
        return morador_id

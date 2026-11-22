from fixhub.domain.permissions import Permissao
from fixhub.domain.usuario import Usuario


class Administrador(Usuario):
    @property
    def perfil(self) -> str:
        return "administrador"

    def tem_permissao(self, permissao: Permissao) -> bool:
        return permissao in {
            Permissao.LISTAR_TODOS_CHAMADOS,
            Permissao.LISTAR_MORADORES,
            Permissao.VER_CONTAGENS,
            Permissao.ALTERAR_ESTADO,
        }

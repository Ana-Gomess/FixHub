from fixhub.domain.permissions import Permissao
from fixhub.domain.usuario import Usuario


class Morador(Usuario):
    @property
    def perfil(self) -> str:
        return "morador"

    def tem_permissao(self, permissao: Permissao) -> bool:
        return permissao in {
            Permissao.CRIAR_CHAMADO,
            Permissao.LISTAR_PROPRIOS_CHAMADOS,
        }

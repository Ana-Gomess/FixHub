from fixhub.domain.errors import SemPermissao
from fixhub.domain.permissions import Permissao
from fixhub.domain.usuario import Usuario
from fixhub.repositories.usuario_repositorio import UsuarioRepositorio


class UsuarioServico:
    """Casos de uso administrativos relacionados a moradores."""

    def __init__(self, usuarios: UsuarioRepositorio):
        self._usuarios = usuarios

    def listar_moradores(self, usuario: Usuario) -> list[dict[str, int | str]]:
        if not usuario.tem_permissao(Permissao.LISTAR_MORADORES):
            raise SemPermissao("Somente administradores podem listar moradores.")
        return self._usuarios.listar_moradores()

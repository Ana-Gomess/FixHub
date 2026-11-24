from domain.errors import SemPermissao
from domain.permissions import Permissao
from domain.usuario import Usuario
from repositories.usuario_repositorio import UsuarioRepositorio


class UsuarioServico:


    def __init__(self, usuarios: UsuarioRepositorio):
        self._usuarios = usuarios

    def listar_moradores(self, usuario: Usuario) -> list[dict[str, int | str]]:
        if not usuario.tem_permissao(Permissao.LISTAR_MORADORES):
            raise SemPermissao("Somente administradores podem listar moradores.")
        return self._usuarios.listar_moradores()

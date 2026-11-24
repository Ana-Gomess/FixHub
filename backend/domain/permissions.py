from enum import Enum


class Permissao(str, Enum):


    CRIAR_CHAMADO = "criar_chamado"
    LISTAR_PROPRIOS_CHAMADOS = "listar_proprios_chamados"
    LISTAR_TODOS_CHAMADOS = "listar_todos_chamados"
    LISTAR_MORADORES = "listar_moradores"
    VER_CONTAGENS = "ver_contagens"
    ALTERAR_ESTADO = "alterar_estado"

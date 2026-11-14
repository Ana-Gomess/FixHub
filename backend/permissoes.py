
from functools import wraps

from flask import g, jsonify, session

from database import conectar_banco


PERFIS_VALIDOS = frozenset({"morador", "administrador"})


def _carregar_usuario_logado():
    if "usuario_atual" in g:
        return g.usuario_atual

    usuario_id = session.get("usuario_id")
    if not isinstance(usuario_id, int):
        session.pop("usuario_id", None)
        return None

    conexao = conectar_banco()
    try:
        registro = conexao.execute(
            """
            SELECT id, nome, email, perfil
            FROM usuarios
            WHERE id = ?
            """,
            (usuario_id,),
        ).fetchone()
    finally:
        conexao.close()

    if registro is None:
        # A conta pode ter sido removida depois da criação da sessão.
        session.pop("usuario_id", None)
        return None

    g.usuario_atual = dict(registro)
    return g.usuario_atual


def requer_login(funcao):

    @wraps(funcao)
    def decorada(*args, **kwargs):
        if _carregar_usuario_logado() is None:
            return jsonify({"erro": "É necessário fazer login."}), 401

        return funcao(*args, **kwargs)

    return decorada


def requer_perfil(*perfis_permitidos):
    if not perfis_permitidos:
        raise ValueError("Informe pelo menos um perfil permitido.")

    perfis_invalidos = set(perfis_permitidos) - PERFIS_VALIDOS
    if perfis_invalidos:
        raise ValueError(
            "Perfil inválido no decorador: " + ", ".join(sorted(perfis_invalidos))
        )

    def decorator(funcao):
        @wraps(funcao)
        @requer_login
        def decorada(*args, **kwargs):
            if g.usuario_atual["perfil"] not in perfis_permitidos:
                return jsonify(
                    {"erro": "Você não tem permissão para acessar este recurso."}
                ), 403

            return funcao(*args, **kwargs)

        return decorada

    return decorator

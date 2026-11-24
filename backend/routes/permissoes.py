
from functools import wraps

from flask import current_app, g, jsonify, session

from domain.permissions import Permissao


PERFIS_VALIDOS = frozenset({"morador", "administrador"})


def _carregar_usuario_logado():
    if "usuario_atual" in g:
        return g.usuario_atual

    usuario_id = session.get("usuario_id")
    if not isinstance(usuario_id, int):
        session.pop("usuario_id", None)
        return None

    usuario = current_app.extensions["fixhub"].autenticacao.buscar_usuario(usuario_id)
    if usuario is None:

        session.pop("usuario_id", None)
        return None

    g.usuario_atual = usuario
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
            if g.usuario_atual.perfil not in perfis_permitidos:
                return jsonify(
                    {"erro": "Você não tem permissão para acessar este recurso."}
                ), 403

            return funcao(*args, **kwargs)

        return decorada

    return decorator


def requer_permissao(permissao: Permissao):


    if not isinstance(permissao, Permissao):
        raise ValueError("Informe uma permissão válida.")

    def decorator(funcao):
        @wraps(funcao)
        @requer_login
        def decorada(*args, **kwargs):
            if not g.usuario_atual.tem_permissao(permissao):
                return jsonify(
                    {"erro": "Você não tem permissão para acessar este recurso."}
                ), 403
            return funcao(*args, **kwargs)

        return decorada

    return decorator

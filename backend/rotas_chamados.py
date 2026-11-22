import sqlite3

from flask import Blueprint, current_app, g, jsonify, request

from fixhub.domain.errors import DadosInvalidos, RecursoNaoEncontrado, SemPermissao
from fixhub.domain.permissions import Permissao
from permissoes import requer_login, requer_permissao


chamados_bp = Blueprint("chamados", __name__)


def _dependencias():
    return current_app.extensions["fixhub"]


def _servico_chamados():
    return _dependencias().servico_chamados


def _servico_painel_chamados():
    return _dependencias().servico_painel_chamados


@chamados_bp.post("/chamados")
@requer_permissao(Permissao.CRIAR_CHAMADO)
def criar_chamado():
    try:
        chamado_criado = _servico_chamados().criar(
            g.usuario_atual, request.get_json(silent=True)
        )
    except DadosInvalidos as erro:
        return jsonify({"erro": str(erro)}), 400
    except SemPermissao as erro:
        return jsonify({"erro": str(erro)}), 403
    except sqlite3.Error:
        return jsonify({"erro": "Não foi possível criar o chamado."}), 500

    return jsonify(
        {
            "mensagem": "Chamado criado com sucesso.",
            "chamado": chamado_criado.para_publico(incluir_morador_id=True),
        }
    ), 201


@chamados_bp.get("/chamados")
@requer_permissao(Permissao.LISTAR_PROPRIOS_CHAMADOS)
def listar_chamados_do_morador():
    try:
        chamados = _servico_chamados().listar_do_morador(g.usuario_atual)
    except DadosInvalidos as erro:
        return jsonify({"erro": str(erro)}), 400
    except SemPermissao as erro:
        return jsonify({"erro": str(erro)}), 403
    except sqlite3.Error:
        return jsonify({"erro": "Não foi possível listar os chamados."}), 500

    return jsonify({"chamados": [item.para_publico() for item in chamados]}), 200


@chamados_bp.get("/chamados/<int:chamado_id>")
@requer_login
def detalhar_chamado(chamado_id: int):
    try:
        dados = _servico_chamados().detalhes(g.usuario_atual, chamado_id)
    except DadosInvalidos as erro:
        return jsonify({"erro": str(erro)}), 400
    except RecursoNaoEncontrado as erro:
        return jsonify({"erro": str(erro)}), 404
    except SemPermissao as erro:
        return jsonify({"erro": str(erro)}), 403
    except sqlite3.Error:
        return jsonify({"erro": "Não foi possível consultar o chamado."}), 500
    return jsonify(dados), 200


@chamados_bp.get("/admin/chamados")
@requer_permissao(Permissao.LISTAR_TODOS_CHAMADOS)
def listar_todos_chamados():
    try:
        chamados = _servico_painel_chamados().listar(
            g.usuario_atual,
            estado=request.args.get("estado"),
            morador_id=request.args.get("morador_id"),
        )
    except DadosInvalidos as erro:
        return jsonify({"erro": str(erro)}), 400
    except SemPermissao as erro:
        return jsonify({"erro": str(erro)}), 403
    except sqlite3.Error:
        return jsonify({"erro": "Não foi possível listar os chamados."}), 500

    return jsonify(
        {
            "chamados": [
                item.para_publico(
                    incluir_morador_id=True, incluir_morador_nome=True
                )
                for item in chamados
            ]
        }
    ), 200


@chamados_bp.get("/admin/chamados/contagens")
@requer_permissao(Permissao.VER_CONTAGENS)
def contar_chamados_por_estado():
    try:
        contagens = _servico_painel_chamados().contar_por_estado(g.usuario_atual)
    except SemPermissao as erro:
        return jsonify({"erro": str(erro)}), 403
    except sqlite3.Error:
        return jsonify({"erro": "Não foi possível contar os chamados."}), 500

    return jsonify({"contagens": contagens}), 200


@chamados_bp.patch("/chamados/<int:chamado_id>/estado")
@requer_permissao(Permissao.ALTERAR_ESTADO)
def alterar_estado_chamado(chamado_id):
    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):
        return jsonify({"erro": "Envie o novo estado em formato JSON."}), 400

    try:
        chamado = _servico_chamados().alterar_estado(
            g.usuario_atual, chamado_id, dados.get("estado")
        )
    except SemPermissao as erro:
        return jsonify({"erro": str(erro)}), 403
    except DadosInvalidos as erro:
        return jsonify({"erro": str(erro)}), 400
    except RecursoNaoEncontrado as erro:
        return jsonify({"erro": str(erro)}), 404
    except sqlite3.Error:
        return jsonify(
            {"erro": "Não foi possível alterar o estado do chamado."}
        ), 500

    return jsonify(
        {
            "mensagem": "Estado do chamado atualizado com sucesso.",
            "chamado": {
                "id": chamado_id,
                "estado": chamado.estado.value,
            },
        }
    ), 200

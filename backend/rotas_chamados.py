import sqlite3

from flask import Blueprint, current_app, g, jsonify, request

from fixhub.domain.chamado import Chamado
from fixhub.domain.errors import DadosInvalidos, RecursoNaoEncontrado, SemPermissao
from fixhub.domain.estado_chamado import EstadoChamado
from fixhub.domain.permissions import Permissao
from permissoes import requer_permissao


chamados_bp = Blueprint("chamados", __name__)


def _dependencias():
    return current_app.extensions["fixhub"]


@chamados_bp.post("/chamados")
@requer_permissao(Permissao.CRIAR_CHAMADO)
def criar_chamado():
    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):
        return jsonify({"erro": "Envie os dados do chamado em formato JSON."}), 400

    campos = ("titulo", "descricao", "localizacao")
    if not all(isinstance(dados.get(campo), str) for campo in campos):
        return jsonify(
            {"erro": "Título, descrição e localização são obrigatórios."}
        ), 400

    valores = {campo: dados[campo].strip() for campo in campos}
    if not all(valores.values()):
        return jsonify(
            {"erro": "Título, descrição e localização são obrigatórios."}
        ), 400

    chamado = Chamado(
        id=None,
        titulo=valores["titulo"],
        descricao=valores["descricao"],
        localizacao=valores["localizacao"],
        morador_id=g.usuario_atual.id,
    )

    try:
        chamado_criado = _dependencias().chamados.salvar(chamado)
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
    morador_id = g.usuario_atual.id
    try:
        chamados = _dependencias().chamados.listar_por_morador(morador_id)
    except sqlite3.Error:
        return jsonify({"erro": "Não foi possível listar os chamados."}), 500

    return jsonify({"chamados": [item.para_publico() for item in chamados]}), 200


@chamados_bp.get("/admin/chamados")
@requer_permissao(Permissao.LISTAR_TODOS_CHAMADOS)
def listar_todos_chamados():
    estado = request.args.get("estado")
    if estado is not None:
        try:
            estado = EstadoChamado.converter(estado)
        except DadosInvalidos as erro:
            return jsonify(
                {"erro": str(erro)}
            ), 400

    morador_id = request.args.get("morador_id")
    if morador_id is not None:
        try:
            morador_id = int(morador_id)
        except ValueError:
            return jsonify(
                {"erro": "O parâmetro morador_id deve ser um inteiro positivo."}
            ), 400

        if morador_id < 1:
            return jsonify(
                {"erro": "O parâmetro morador_id deve ser um inteiro positivo."}
            ), 400

    try:
        chamados = _dependencias().chamados.listar_todos(estado, morador_id)
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
        contagens = _dependencias().chamados.contar_por_estado()
    except sqlite3.Error:
        return jsonify({"erro": "Não foi possível contar os chamados."}), 500

    return jsonify({"contagens": contagens}), 200


@chamados_bp.patch("/chamados/<int:chamado_id>/estado")
@requer_permissao(Permissao.ALTERAR_ESTADO)
def alterar_estado_chamado(chamado_id):
    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):
        return jsonify({"erro": "Envie o novo estado em formato JSON."}), 400

    novo_estado = dados.get("estado")
    if not isinstance(novo_estado, str) or not novo_estado.strip():
        return jsonify({"erro": "O estado é obrigatório."}), 400

    try:
        dependencias = _dependencias()
        with dependencias.database.transacao() as conexao:
            chamado = dependencias.chamados.buscar_por_id(chamado_id, conexao)
            if chamado is None:
                return jsonify({"erro": "Chamado não encontrado."}), 404

            historico = chamado.transicionar_para(novo_estado, g.usuario_atual)
            dependencias.chamados.atualizar_estado(chamado, conexao)
            dependencias.historicos.salvar(historico, conexao)
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

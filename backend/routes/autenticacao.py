import sqlite3

from flask import Blueprint, current_app, g, jsonify, request, session

from domain.errors import (
    CredenciaisInvalidas,
    DadosInvalidos,
    EmailDuplicado,
)
from domain.morador import BLOCOS_DISPONIVEIS
from routes.permissoes import requer_login


autenticacao_bp = Blueprint("autenticacao", __name__)


def _servico():
    return current_app.extensions["fixhub"].autenticacao


@autenticacao_bp.get("/blocos")
def listar_blocos():
    return jsonify({"blocos": BLOCOS_DISPONIVEIS}), 200


@autenticacao_bp.post("/usuarios")
def cadastrar_usuario():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify({"erro": "Envie os dados do cadastro em formato JSON."}), 400

    perfil = dados.get("perfil", "morador")
    if not isinstance(perfil, str):
        return jsonify({"erro": "O perfil deve ser um texto."}), 400
    perfil = perfil.strip().lower()
    if perfil not in {"morador", "administrador"}:
        return jsonify({"erro": "Perfil inválido."}), 400
    if perfil == "administrador":
        return jsonify(
            {"erro": "O cadastro público permite apenas o perfil morador."}
        ), 403

    try:
        usuario = _servico().cadastrar_morador(
            dados.get("nome"),
            dados.get("email"),
            dados.get("senha"),
            dados.get("bloco"),
        )
    except EmailDuplicado as erro:
        return jsonify({"erro": str(erro)}), 409
    except DadosInvalidos as erro:
        return jsonify({"erro": str(erro)}), 400
    except sqlite3.Error:
        return jsonify({"erro": "Não foi possível criar a conta."}), 500

    return jsonify(
        {
            "mensagem": "Cadastro realizado com sucesso.",
            "usuario": usuario.para_publico(),
        }
    ), 201


@autenticacao_bp.post("/login")
def fazer_login():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify({"erro": "Envie e-mail e senha em formato JSON."}), 400

    try:
        usuario = _servico().autenticar(dados.get("email"), dados.get("senha"))
    except CredenciaisInvalidas as erro:
        return jsonify({"erro": str(erro)}), 401
    except DadosInvalidos as erro:
        return jsonify({"erro": str(erro)}), 400
    except sqlite3.Error:
        return jsonify({"erro": "Não foi possível consultar a conta."}), 500

    session.clear()
    session["usuario_id"] = usuario.id
    return jsonify(
        {
            "mensagem": "Login realizado com sucesso.",
            "usuario": usuario.para_publico(),
        }
    ), 200


@autenticacao_bp.post("/logout")
def fazer_logout():
    session.clear()
    return jsonify({"mensagem": "Logout realizado com sucesso."}), 200


@autenticacao_bp.get("/sessao")
@requer_login
def obter_sessao():
    return jsonify({"usuario": g.usuario_atual.para_publico()}), 200

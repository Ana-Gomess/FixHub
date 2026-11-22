import re
import sqlite3

from flask import Blueprint, current_app, jsonify, request, session

from fixhub.domain.errors import DadosInvalidos
from fixhub.domain.morador import Morador


autenticacao_bp = Blueprint("autenticacao", __name__)
FORMATO_EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


def _usuarios():
    return current_app.extensions["fixhub"].usuarios


@autenticacao_bp.post("/usuarios")
def cadastrar_usuario():
    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):
        return jsonify({"erro": "Envie os dados do cadastro em formato JSON."}), 400

    nome = dados.get("nome")
    email = dados.get("email")
    senha = dados.get("senha")
    perfil = dados.get("perfil", "morador")

    if not all(isinstance(valor, str) for valor in (nome, email, senha, perfil)):
        return jsonify({"erro": "Nome, e-mail, senha e perfil devem ser textos."}), 400

    nome = nome.strip()
    email = email.strip().lower()
    perfil = perfil.strip().lower()

    if not nome or not email or not senha.strip():
        return jsonify({"erro": "Nome, e-mail e senha são obrigatórios."}), 400

    if not FORMATO_EMAIL.fullmatch(email):
        return jsonify({"erro": "Informe um e-mail válido."}), 400

    if perfil not in {"morador", "administrador"}:
        return jsonify({"erro": "Perfil inválido."}), 400

    # O cadastro público só cria moradores.
    if perfil != "morador":
        return jsonify(
            {"erro": "Esse cadastro permite apenas o perfil morador."}
        ), 403

    try:
        usuario = Morador.criar_com_senha(nome=nome, email=email, senha=senha)
        usuario = _usuarios().salvar(usuario)
    except DadosInvalidos as erro:
        return jsonify({"erro": str(erro)}), 400
    except sqlite3.IntegrityError:
        return jsonify({"erro": "Este e-mail já está cadastrado."}), 409
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

    email = dados.get("email")
    senha = dados.get("senha")

    if not isinstance(email, str) or not isinstance(senha, str):
        return jsonify({"erro": "E-mail e senha devem ser textos."}), 400

    email = email.strip().lower()

    if not email or not senha.strip():
        return jsonify({"erro": "E-mail e senha são obrigatórios."}), 400

    try:
        usuario = _usuarios().buscar_por_email(email)
    except sqlite3.Error:
        return jsonify({"erro": "Não foi possível consultar a conta."}), 500

    if usuario is None:
        return jsonify({"erro": "E-mail ou senha incorretos."}), 401

    if not usuario.verificar_senha(senha):
        return jsonify({"erro": "E-mail ou senha incorretos."}), 401

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

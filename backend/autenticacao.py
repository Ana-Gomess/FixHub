import re
import sqlite3

from flask import Blueprint, jsonify, request

from database import conectar_banco
from usuario import Usuario


autenticacao_bp = Blueprint("autenticacao", __name__)
FORMATO_EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


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

    # O cadastro público só cria moradores; administradores devem ser cadastrados
    # por um fluxo controlado, para evitar elevação de privilégio.
    if perfil != "morador":
        return jsonify({"erro": "Esse cadastro permite apenas o perfil morador."}), 403

    usuario = Usuario(nome=nome, email=email, senha=senha, perfil="morador")
    conexao = conectar_banco()
    try:
        cursor = conexao.execute(
            "INSERT INTO usuarios (nome, email, senha_hash, perfil) VALUES (?, ?, ?, ?)",
            (usuario.nome, usuario.email, usuario.senha_hash, usuario.perfil),
        )
        conexao.commit()
        usuario_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        conexao.rollback()
        return jsonify({"erro": "Este e-mail já está cadastrado."}), 409
    finally:
        conexao.close()

    return jsonify(
        {
            "mensagem": "Cadastro realizado com sucesso.",
            "usuario": {
                "id": usuario_id,
                "nome": usuario.nome,
                "email": usuario.email,
                "perfil": usuario.perfil,
            },
        }
    ), 201

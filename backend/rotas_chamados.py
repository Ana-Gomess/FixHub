import sqlite3

from flask import Blueprint, g, jsonify, request

from chamado import Chamado
from database import conectar_banco
from permissoes import requer_perfil


chamados_bp = Blueprint("chamados", __name__)


@chamados_bp.post("/chamados")
@requer_perfil("morador")
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
        titulo=valores["titulo"],
        descricao=valores["descricao"],
        localizacao=valores["localizacao"],
        morador_id=g.usuario_atual["id"],
    )

    conexao = conectar_banco()
    try:
        cursor = conexao.execute(
            """
            INSERT INTO chamados (titulo, descricao, localizacao, estado, morador_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                chamado.titulo,
                chamado.descricao,
                chamado.localizacao,
                chamado.estado,
                chamado.morador_id,
            ),
        )
        conexao.commit()
        chamado_id = cursor.lastrowid
    except sqlite3.Error:
        conexao.rollback()
        return jsonify({"erro": "Não foi possível criar o chamado."}), 500
    finally:
        conexao.close()

    return jsonify(
        {
            "mensagem": "Chamado criado com sucesso.",
            "chamado": {
                "id": chamado_id,
                "titulo": chamado.titulo,
                "descricao": chamado.descricao,
                "localizacao": chamado.localizacao,
                "estado": chamado.estado,
                "morador_id": chamado.morador_id,
            },
        }
    ), 201

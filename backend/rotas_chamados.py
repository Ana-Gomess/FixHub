import sqlite3

from flask import Blueprint, g, jsonify, request

from chamado import Chamado
from database import conectar_banco
from permissoes import requer_perfil


chamados_bp = Blueprint("chamados", __name__)

ESTADOS_VALIDOS = {"Aberto", "Em Análise", "Resolvido"}
TRANSICOES_PERMITIDAS = {
    "Aberto": {"Em Análise", "Resolvido"},
    "Em Análise": {"Resolvido"},
    "Resolvido": set(),
}


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


@chamados_bp.get("/chamados")
@requer_perfil("morador")
def listar_chamados_do_morador():
    morador_id = g.usuario_atual["id"]
    conexao = conectar_banco()
    try:
        registros = conexao.execute(
            """
            SELECT id, titulo, descricao, localizacao, estado
            FROM chamados
            WHERE morador_id = ?
            ORDER BY id DESC
            """,
            (morador_id,),
        ).fetchall()
    except sqlite3.Error:
        return jsonify({"erro": "Não foi possível listar os chamados."}), 500
    finally:
        conexao.close()

    return jsonify({"chamados": [dict(registro) for registro in registros]}), 200


@chamados_bp.get("/admin/chamados")
@requer_perfil("administrador")
def listar_todos_chamados():
    conexao = conectar_banco()
    try:
        registros = conexao.execute(
            """
            SELECT
                chamados.id,
                chamados.titulo,
                chamados.descricao,
                chamados.localizacao,
                chamados.estado,
                chamados.morador_id,
                usuarios.nome AS morador_nome
            FROM chamados
                     JOIN usuarios ON usuarios.id = chamados.morador_id
            ORDER BY chamados.id DESC
            """
        ).fetchall()
    except sqlite3.Error:
        return jsonify({"erro": "Não foi possível listar os chamados."}), 500
    finally:
        conexao.close()

    return jsonify(
        {"chamados": [dict(registro) for registro in registros]}
    ), 200


@chamados_bp.patch("/chamados/<int:chamado_id>/estado")
@requer_perfil("administrador")
def alterar_estado_chamado(chamado_id):
    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):
        return jsonify({"erro": "Envie o novo estado em formato JSON."}), 400

    estado = dados.get("estado")
    if not isinstance(estado, str) or not estado.strip():
        return jsonify({"erro": "O estado é obrigatório."}), 400

    estado = estado.strip()
    if estado not in ESTADOS_VALIDOS:
        return jsonify(
            {
                "erro": (
                    "Estado inválido. Use: Aberto, Em Análise ou Resolvido."
                )
            }
        ), 400

    conexao = conectar_banco()
    try:
        registro = conexao.execute(
            "SELECT estado FROM chamados WHERE id = ?",
            (chamado_id,),
        ).fetchone()

        if registro is None:
            return jsonify({"erro": "Chamado não encontrado."}), 404

        estado_atual = registro["estado"]
        if estado not in TRANSICOES_PERMITIDAS.get(estado_atual, set()):
            return jsonify(
                {
                    "erro": (
                        f"Não é permitido alterar o estado de "
                        f"'{estado_atual}' para '{estado}'."
                    )
                }
            ), 400

        cursor = conexao.execute(
            "UPDATE chamados SET estado = ? WHERE id = ?",
            (estado, chamado_id),
        )
        if cursor.rowcount == 0:
            return jsonify({"erro": "Chamado não encontrado."}), 404

        conexao.execute(
            """
            INSERT INTO historico_estados (
                chamado_id,
                estado_anterior,
                estado_novo,
                administrador_id
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                chamado_id,
                estado_atual,
                estado,
                g.usuario_atual["id"],
            ),
        )

        conexao.commit()
    except sqlite3.Error:
        conexao.rollback()
        return jsonify(
            {"erro": "Não foi possível alterar o estado do chamado."}
        ), 500
    finally:
        conexao.close()

    return jsonify(
        {
            "mensagem": "Estado do chamado atualizado com sucesso.",
            "chamado": {
                "id": chamado_id,
                "estado": estado,
            },
        }
    ), 200
import sqlite3

from flask import Blueprint, g, jsonify, request

from database import conectar_banco
from fixhub.domain.chamado import Chamado
from fixhub.domain.errors import DadosInvalidos, SemPermissao
from fixhub.domain.estado_chamado import EstadoChamado
from fixhub.domain.permissions import Permissao
from permissoes import requer_permissao


chamados_bp = Blueprint("chamados", __name__)


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
                chamado.estado.value,
                chamado.morador_id,
            ),
        )
        conexao.commit()
        chamado_criado = chamado.com_id(cursor.lastrowid)
    except sqlite3.Error:
        conexao.rollback()
        return jsonify({"erro": "Não foi possível criar o chamado."}), 500
    finally:
        conexao.close()

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
@requer_permissao(Permissao.LISTAR_TODOS_CHAMADOS)
def listar_todos_chamados():
    filtros = []
    parametros = []

    estado = request.args.get("estado")
    if estado is not None:
        try:
            estado = EstadoChamado.converter(estado)
        except DadosInvalidos as erro:
            return jsonify(
                {"erro": str(erro)}
            ), 400

        filtros.append("chamados.estado = ?")
        parametros.append(estado.value)

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

        filtros.append("chamados.morador_id = ?")
        parametros.append(morador_id)

    consulta = """
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
    """
    if filtros:
        consulta += " WHERE " + " AND ".join(filtros)
    consulta += " ORDER BY chamados.id DESC"

    conexao = conectar_banco()
    try:
        registros = conexao.execute(consulta, parametros).fetchall()
    except sqlite3.Error:
        return jsonify({"erro": "Não foi possível listar os chamados."}), 500
    finally:
        conexao.close()

    return jsonify(
        {"chamados": [dict(registro) for registro in registros]}
    ), 200


@chamados_bp.get("/admin/chamados/contagens")
@requer_permissao(Permissao.VER_CONTAGENS)
def contar_chamados_por_estado():
    conexao = conectar_banco()
    try:
        registro = conexao.execute(
            """
            SELECT
                COUNT(CASE WHEN estado = 'Aberto' THEN 1 END) AS abertos,
                COUNT(CASE WHEN estado = 'Em Análise' THEN 1 END) AS em_analise,
                COUNT(CASE WHEN estado = 'Resolvido' THEN 1 END) AS resolvidos
            FROM chamados
            """
        ).fetchone()
    except sqlite3.Error:
        return jsonify({"erro": "Não foi possível contar os chamados."}), 500
    finally:
        conexao.close()

    return jsonify({"contagens": dict(registro)}), 200


@chamados_bp.patch("/chamados/<int:chamado_id>/estado")
@requer_permissao(Permissao.ALTERAR_ESTADO)
def alterar_estado_chamado(chamado_id):
    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):
        return jsonify({"erro": "Envie o novo estado em formato JSON."}), 400

    novo_estado = dados.get("estado")
    if not isinstance(novo_estado, str) or not novo_estado.strip():
        return jsonify({"erro": "O estado é obrigatório."}), 400

    conexao = conectar_banco()
    try:
        registro = conexao.execute(
            """
            SELECT id, titulo, descricao, localizacao, estado, morador_id
            FROM chamados WHERE id = ?
            """,
            (chamado_id,),
        ).fetchone()

        if registro is None:
            return jsonify({"erro": "Chamado não encontrado."}), 404

        chamado = Chamado(
            id=registro["id"],
            titulo=registro["titulo"],
            descricao=registro["descricao"],
            localizacao=registro["localizacao"],
            morador_id=registro["morador_id"],
            estado=EstadoChamado.converter(registro["estado"]),
        )
        try:
            historico = chamado.transicionar_para(
                novo_estado, g.usuario_atual
            )
        except SemPermissao as erro:
            conexao.rollback()
            return jsonify({"erro": str(erro)}), 403
        except DadosInvalidos as erro:
            conexao.rollback()
            return jsonify({"erro": str(erro)}), 400

        cursor = conexao.execute(
            "UPDATE chamados SET estado = ? WHERE id = ?",
            (chamado.estado.value, chamado_id),
        )
        if cursor.rowcount == 0:
            return jsonify({"erro": "Chamado não encontrado."}), 404

        conexao.execute(
            """
            INSERT INTO historico_estados (
                chamado_id,
                estado_anterior,
                estado_novo,
                administrador_id,
                data_hora
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                chamado_id,
                historico.estado_anterior.value,
                historico.estado_novo.value,
                historico.administrador_id,
                historico.data_hora.isoformat(),
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
                "estado": chamado.estado.value,
            },
        }
    ), 200

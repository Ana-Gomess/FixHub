"""Páginas HTML servidas pelo Flask."""

from flask import Blueprint, render_template


paginas_bp = Blueprint("paginas", __name__)


@paginas_bp.get("/cadastro")
def pagina_cadastro():
    return render_template("cadastro.html")


@paginas_bp.get("/login")
def pagina_login():
    return render_template("login.html")


@paginas_bp.get("/chamados/novo")
def pagina_novo_chamado():
    return render_template("chamado_novo.html")


@paginas_bp.get("/meus-chamados")
def pagina_meus_chamados():
    return render_template("meus_chamados.html")


@paginas_bp.get("/painel-admin")
def pagina_painel_admin():
    return render_template("painel_admin.html")


@paginas_bp.get("/chamados/<int:chamado_id>/detalhes")
def pagina_detalhe_chamado(chamado_id: int):
    return render_template("detalhe_chamado.html", chamado_id=chamado_id)

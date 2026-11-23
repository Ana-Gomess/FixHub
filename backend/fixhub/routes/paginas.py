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

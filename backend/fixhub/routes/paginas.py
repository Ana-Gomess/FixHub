"""Páginas HTML servidas pelo Flask."""

from flask import Blueprint, render_template


paginas_bp = Blueprint("paginas", __name__)


@paginas_bp.get("/cadastro")
def pagina_cadastro():
    return render_template("cadastro.html")

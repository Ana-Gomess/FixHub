

from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from flask import Flask


def create_app(config: dict[str, Any] | None = None) -> Flask:






    from routes.autenticacao import autenticacao_bp
    from routes.chamados import chamados_bp
    from infrastructure.database import Database
    from repositories.chamado_repositorio import ChamadoRepositorio
    from repositories.historico_repositorio import HistoricoRepositorio
    from repositories.usuario_repositorio import UsuarioRepositorio
    from services.autenticacao_servico import AutenticacaoServico
    from services.chamado_servico import ChamadoServico
    from services.painel_chamados_servico import PainelChamadosServico
    from services.usuario_servico import UsuarioServico

    backend_dir = Path(__file__).resolve().parent
    project_dir = backend_dir.parent
    app = Flask(
        "fixhub",
        template_folder=str(project_dir / "frontend" / "templates"),
        static_folder=str(project_dir / "frontend" / "static"),
        static_url_path="/static",
    )
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("FLASK_SECRET_KEY"),
        DATABASE_PATH=os.environ.get(
            "FIXHUB_DATABASE", str(backend_dir / "fixhub.db")
        ),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )
    if config:
        app.config.update(config)

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError(
            "Configure FLASK_SECRET_KEY antes de iniciar o FixHub. "
            "No PowerShell: $env:FLASK_SECRET_KEY = (python -c "
            '"import secrets; print(secrets.token_hex(32))")'
        )

    banco = Database(app.config["DATABASE_PATH"])
    banco.inicializar()

    usuarios = UsuarioRepositorio(banco)
    chamados = ChamadoRepositorio(banco)
    historicos = HistoricoRepositorio(banco)
    app.extensions["fixhub"] = SimpleNamespace(
        database=banco,
        usuarios=usuarios,
        chamados=chamados,
        historicos=historicos,
        autenticacao=AutenticacaoServico(usuarios),
        servico_chamados=ChamadoServico(banco, chamados, historicos),
        servico_painel_chamados=PainelChamadosServico(chamados),
        servico_usuarios=UsuarioServico(usuarios),
    )

    from routes.paginas import paginas_bp

    app.register_blueprint(autenticacao_bp)
    app.register_blueprint(chamados_bp)
    app.register_blueprint(paginas_bp)
    return app


__all__ = ["create_app"]

"""Factory e composição da aplicação Flask FixHub."""

from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from flask import Flask


def create_app(config: dict[str, Any] | None = None) -> Flask:
    """Cria e configura a aplicação sem iniciá-la durante a importação.

    ``config`` permite substituir as configurações padrão, por exemplo em
    outros ambientes. A persistência é conectada aos repositórios por esta
    composição; as rotas ainda orquestram as operações até a task de serviços.
    """
    from autenticacao import autenticacao_bp
    from rotas_chamados import chamados_bp
    from fixhub.infrastructure.database import Database
    from fixhub.repositories.chamado_repositorio import ChamadoRepositorio
    from fixhub.repositories.historico_repositorio import HistoricoRepositorio
    from fixhub.repositories.usuario_repositorio import UsuarioRepositorio
    from fixhub.services.autenticacao_servico import AutenticacaoServico
    from fixhub.services.chamado_servico import ChamadoServico

    backend_dir = Path(__file__).resolve().parents[1]
    app = Flask(__name__, static_folder=None)
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
        servico_chamados=ChamadoServico(chamados, historicos),
    )

    app.register_blueprint(autenticacao_bp)
    app.register_blueprint(chamados_bp)
    return app


__all__ = ["create_app"]

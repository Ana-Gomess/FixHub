"""Factory e composição da aplicação Flask FixHub."""

from __future__ import annotations

import os
from typing import Any

from flask import Flask


def create_app(config: dict[str, Any] | None = None) -> Flask:
    """Cria e configura a aplicação sem iniciá-la durante a importação.

    ``config`` permite substituir as configurações padrão, por exemplo em
    ambientes de desenvolvimento ou em futuras verificações automatizadas.
    As rotas e o banco permanecem nos módulos atuais nesta primeira etapa de
    refatoração; serão migrados para ``fixhub`` nas tasks seguintes.
    """
    from autenticacao import autenticacao_bp
    from database import inicializar_banco
    from rotas_chamados import chamados_bp

    app = Flask(__name__, static_folder=None)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("FLASK_SECRET_KEY"),
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

    inicializar_banco()
    app.register_blueprint(autenticacao_bp)
    app.register_blueprint(chamados_bp)
    return app


__all__ = ["create_app"]

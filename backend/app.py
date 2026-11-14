import os

from flask import Flask
from autenticacao import autenticacao_bp
from rotas_chamados import chamados_bp
from database import inicializar_banco

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ["FLASK_SECRET_KEY"]

inicializar_banco()
app.register_blueprint(autenticacao_bp)
app.register_blueprint(chamados_bp)

if __name__ == "__main__":
    app.run(debug=True)

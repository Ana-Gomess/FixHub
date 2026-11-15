import os

from flask import Flask, render_template
from autenticacao import autenticacao_bp
from rotas_chamados import chamados_bp
from database import inicializar_banco
from permissoes import requer_perfil

app = Flask(__name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static")
app.config["SECRET_KEY"] = os.environ["FLASK_SECRET_KEY"]

inicializar_banco()
app.register_blueprint(autenticacao_bp)
app.register_blueprint(chamados_bp)

@app.route("/cadastro")
def pagina_cadastro():
    return render_template("cadastro.html")

@app.route("/login", methods=["GET"])
def pagina_login():
    return render_template("login.html")

@app.route("/chamado/novo")
@requer_perfil("morador")
def pagina_novo_chamado():
    return render_template("chamado_novo.html")

@app.route("/admin")
@requer_perfil("administrador")
def pagina_admin():
    return render_template("admin.html")

if __name__ == "__main__":
    app.run(debug=True)

"""Ponto de entrada do servidor Flask do FixHub."""

from fixhub import create_app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)

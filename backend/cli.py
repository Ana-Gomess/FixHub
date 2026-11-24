

import argparse
import getpass
import os
from pathlib import Path
import sqlite3

from domain.errors import DadosInvalidos, EmailDuplicado
from infrastructure.database import Database
from repositories.usuario_repositorio import UsuarioRepositorio
from services.autenticacao_servico import AutenticacaoServico


def criar_administrador() -> int:
    backend_dir = Path(__file__).resolve().parent
    caminho_banco = os.environ.get(
        "FIXHUB_DATABASE", str(backend_dir / "fixhub.db")
    )
    banco = Database(caminho_banco)
    banco.inicializar()
    servico = AutenticacaoServico(UsuarioRepositorio(banco))

    print("Criar conta local de administrador do FixHub")
    nome = input("Nome: ")
    email = input("E-mail: ")
    senha = getpass.getpass("Senha: ")
    confirmacao = getpass.getpass("Confirme a senha: ")
    if senha != confirmacao:
        print("As senhas não conferem.")
        return 1

    try:
        administrador = servico.criar_administrador(nome, email, senha)
    except (DadosInvalidos, EmailDuplicado) as erro:
        print(f"Não foi possível criar o administrador: {erro}")
        return 1
    except sqlite3.Error:
        print("Não foi possível acessar o banco de dados local.")
        return 1

    print(f"Administrador criado: {administrador.email}")
    print("A senha foi armazenada como hash e não foi gravada no código.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Ferramentas locais do FixHub")
    parser.add_argument(
        "comando", choices=["criar-admin"], help="comando administrativo"
    )
    argumentos = parser.parse_args()
    if argumentos.comando == "criar-admin":
        return criar_administrador()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

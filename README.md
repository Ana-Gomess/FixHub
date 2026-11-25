# FixHub

Sistema web para moradores registrarem problemas de manutenção e para administradores acompanharem e atualizarem os chamados.

## Tecnologias

- Python 3.10 ou superior, Flask e SQLite no back-end.
- HTML, CSS e JavaScript no front-end, servido pelo Flask.

## Instalar o Flask pelo terminal do VS Code

No terminal PowerShell do VS Code, a partir da raiz do repositório:

1. Entre na pasta `backend`:
   ```powershell
   cd backend
   ```
2. Crie um ambiente virtual para manter as bibliotecas do projeto separadas:
   ```powershell
   python -m venv .venv
   ```
3. Ative o ambiente virtual:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   O terminal mostrará `(.venv)` quando ele estiver ativo.
4. Instale o Flask e as dependências listadas em `requirements.txt`:
   ```powershell
   python -m pip install -r requirements.txt
   ```

## Iniciar o servidor

Ainda dentro de `backend`, com `(.venv)` ativo, configure a chave da sessão e inicie o servidor:

```powershell
$env:FLASK_SECRET_KEY = (python -c "import secrets; print(secrets.token_hex(32))")
python app.py
```

A chave `FLASK_SECRET_KEY` protege a sessão do Flask. Não a publique nem a adicione ao Git. Para encerrar o servidor, pressione `Ctrl+C` no terminal.

Para criar um administrador local, execute `python -m cli criar-admin`. O comando solicita nome, e-mail e senha. O cadastro público cria somente contas de morador.

## Rotas da interface

- Cadastro: <http://127.0.0.1:5000/cadastro>
- Login: <http://127.0.0.1:5000/login>
- Painel administrativo: <http://127.0.0.1:5000/painel-admin> (administrador autenticado)

## Organização do código

```text
backend/
  app.py                 Inicializa o servidor
  app_factory.py         Monta e configura a aplicação Flask
  cli.py                 Comandos administrativos locais
  domain/                Entidades e regras do domínio
  infrastructure/        Conexão, transações e esquema SQLite
  repositories/          Leitura e gravação dos dados
  routes/                Rotas HTTP e páginas
  services/              Casos de uso e coordenação das regras
frontend/
  templates/             Páginas HTML
  static/css/            Estilos
  static/js/             Comportamento das páginas
```

## Rotas principais da API

- Cadastro: `GET /blocos` lista A–F; `POST /usuarios` cria a conta com o bloco escolhido.
- Autenticação: `POST /login`, `POST /logout` e `GET /sessao`.
- Morador: `POST /chamados`, `GET /chamados` e `GET /chamados/<id>`.
- Administração: `GET /admin/chamados`, `GET /admin/chamados/contagens` e `GET /admin/moradores`.
- Atualização de estado: `PATCH /chamados/<id>/estado`.

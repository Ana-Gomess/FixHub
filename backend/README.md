# Back-end do FixHub

## Instalar o Flask pelo terminal do VS Code

1. Entre na pasta `backend`:
   `cd backend`

2. Crie um ambiente virtual para manter as bibliotecas deste projeto separadas:
   `python -m venv .venv`

3. Ative o ambiente virtual no PowerShell do VS Code:
   `.\.venv\Scripts\Activate.ps1`
   O terminal mostrará `(.venv)` quando ele estiver ativo.

4. Instale o Flask e os pacotes listados em `requirements.txt`:
   `python -m pip install -r requirements.txt`

## Proteção de rotas por perfil

Use os decoradores de `permissoes.py` nas rotas que exigem autenticação:

```python
from flask import g, jsonify
from permissoes import requer_login, requer_perfil

@chamados_bp.get("/chamados")
@requer_login
def listar_chamados():
    return jsonify({"usuario_id": g.usuario_atual["id"]})

@chamados_bp.get("/painel")
@requer_perfil("administrador")
def painel_administrador():
    return jsonify({"mensagem": "Acesso administrativo autorizado."})
```

`requer_login` responde `401` quando não há sessão válida. `requer_perfil` também
exige login e responde `403` quando o usuário autenticado não tem um dos perfis
permitidos. Para permitir ambos os perfis em uma rota, use
`@requer_perfil("morador", "administrador")`.

## Executar os testes

No terminal, entre nesta pasta (`backend`) e execute:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

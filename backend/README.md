# Back-end do FixHub

## Factory e pacote modular

`app.py` importa `create_app` do pacote `fixhub`. A factory configura a chave de
sessão, inicializa o SQLite e compõe os repositórios que serão usados pelas
rotas. Ela também aceita um dicionário de configurações para substituir os
valores padrão.

As pastas `fixhub/domain`, `fixhub/infrastructure`, `fixhub/repositories`,
`fixhub/services` e `fixhub/routes` organizam o sistema em camadas. A conexão,
as transações e as consultas SQLite ficam em `infrastructure/database.py` e
`repositories/`. As rotas de cadastro e login usam `AutenticacaoServico`; as
operações de criação, lista e detalhes dos chamados do morador usam
`ChamadoServico`. O painel administrativo e a alteração de estado ainda chamam
os repositórios diretamente; serão migrados nas próximas tasks.

## Iniciar o servidor

Execute os comandos no PowerShell, dentro da pasta `backend`. Crie e ative o
ambiente virtual e instale as dependências na primeira execução:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Configure uma chave de sessão no mesmo terminal e inicie o servidor:

```powershell
$env:FLASK_SECRET_KEY = (python -c "import secrets; print(secrets.token_hex(32))")
python app.py
```

Abra `http://127.0.0.1:5000`. Não publique nem versione o valor de
`FLASK_SECRET_KEY`. Se fechar o terminal, gere outra chave ou reutilize uma
guardada localmente.

Para criar uma conta administrativa local, execute na pasta `backend`:

```powershell
python -m fixhub.cli criar-admin
```

O comando pede nome, e-mail e senha. A senha não fica no código; o administrador
é salvo no SQLite local.

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

`Usuario` é a classe abstrata de conta. `Morador` e `Administrador` herdam seus
dados e definem permissões diferentes. As rotas protegidas consultam
`tem_permissao`, então cada objeto responde conforme o seu tipo concreto:

```python
from fixhub.domain.permissions import Permissao
from permissoes import requer_permissao

@chamados_bp.get("/chamados")
@requer_permissao(Permissao.LISTAR_PROPRIOS_CHAMADOS)
def listar_chamados():
    ...
```

`requer_permissao` responde `401` quando não há sessão válida e `403` quando o
usuário não tem a permissão solicitada. `requer_perfil` permanece como helper
de compatibilidade.

O hash da senha fica encapsulado em `Usuario`, é usado por
`verificar_senha` durante o login e não faz parte de `para_publico()`. O cadastro
público instancia `Morador`; não é possível escolher o perfil de administrador.
Cadastro e autenticação passam pelo serviço `AutenticacaoServico`. A rota
`GET /sessao` devolve os dados públicos do usuário autenticado.

## Domínio de chamados

`Chamado` valida título, descrição, localização e vínculo com o morador. Os
estados são representados por `EstadoChamado`, que concentra as transições
permitidas: `Aberto` pode ir para `Em Análise` ou `Resolvido`; `Em Análise` pode
ir para `Resolvido`; `Resolvido` é final. O método `transicionar_para` exige um
administrador autorizado e retorna um `HistoricoEstado` imutável com os dados
da mudança. O serviço do morador consulta e persiste chamados pelos repositórios.
O painel e a alteração de estado ainda usam repositórios diretamente; essa
orquestração será migrada nas tasks seguintes.

## Criar chamado

A rota `POST /chamados` exige uma sessão de morador e recebe JSON com `titulo`,
`descricao` e `localizacao`. O estado inicial é `Aberto`, e o morador responsável
é definido pelo usuário autenticado, sem aceitar esses valores do cliente.

Exemplo de corpo:

```json
{
  "titulo": "Vazamento na cozinha",
  "descricao": "Há água saindo do sifão.",
  "localizacao": "Apartamento 12"
}
```

## Listar chamados do morador

A rota `GET /chamados` exige perfil `morador` e retorna somente os chamados do
usuário autenticado, incluindo o estado atual. Se ele ainda não tiver chamados,
a resposta contém uma lista vazia.

`GET /chamados/<id>` retorna os detalhes e o histórico se o chamado pertence ao
morador autenticado. Um administrador também pode consultar os detalhes. Para
outros usuários, a API responde `404`.

## Painel de chamados do administrador

`GET /admin/chamados` exige perfil `administrador` e retorna a lista geral de
chamados com o nome do morador. Os filtros opcionais `estado` e `morador_id`
podem ser usados juntos. `PainelChamadosServico` valida os filtros e consulta o
repositório. Exemplos: `/admin/chamados?estado=Aberto` e
`/admin/chamados?estado=Resolvido&morador_id=3`.

`GET /admin/chamados/contagens` retorna a quantidade total de chamados em cada
estado (`abertos`, `em_analise` e `resolvidos`) e também exige perfil
`administrador`. A consulta é coordenada por `PainelChamadosServico`.

`GET /admin/moradores` exige perfil `administrador` e retorna os moradores em
ordem alfabética, com `id` e `nome`, para preencher o filtro do painel.

## Alterar estado do chamado

A rota `PATCH /chamados/<id>/estado` exige perfil administrador e recebe o novo
estado no JSON. `ChamadoServico` aplica a transição e grava o estado e o
histórico na mesma transação. As transições permitidas são `Aberto` para
`Em Análise` ou `Resolvido`, e `Em Análise` para `Resolvido`. `Resolvido` é um
estado final.


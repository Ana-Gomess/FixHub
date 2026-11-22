# Back-end do FixHub

## Factory e pacote modular

`app.py` importa `create_app` do pacote `fixhub`. A factory configura a chave de
sessão, inicializa o banco existente e registra os blueprints de autenticação e
chamados. Ela também aceita um dicionário de configurações para substituir os
valores padrão.

As pastas `fixhub/domain`, `fixhub/infrastructure`, `fixhub/repositories`,
`fixhub/services` e `fixhub/routes` iniciam a organização em camadas. Nesta
task, os módulos de domínio, banco e rotas ainda permanecem na raiz de
`backend`; sua migração para os pacotes ocorrerá nas tasks seguintes.

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
usuário não tem a permissão solicitada. `requer_perfil` continua disponível nas
rotas antigas enquanto elas são migradas.

O hash da senha fica encapsulado em `Usuario`, é usado por
`verificar_senha` durante o login e não faz parte de `para_publico()`. O cadastro
público instancia `Morador`; não é possível escolher o perfil de administrador.

## Domínio de chamados

`Chamado` valida título, descrição, localização e vínculo com o morador. Os
estados são representados por `EstadoChamado`, que concentra as transições
permitidas: `Aberto` pode ir para `Em Análise` ou `Resolvido`; `Em Análise` pode
ir para `Resolvido`; `Resolvido` é final. O método `transicionar_para` exige um
administrador autorizado e retorna um `HistoricoEstado` imutável com os dados
da mudança. A rota continua persistindo esses dados diretamente no SQLite
nesta etapa; a migração para serviços e repositórios é feita nas tasks seguintes.

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

## Painel de chamados do administrador

`GET /admin/chamados` exige perfil `administrador` e retorna a lista geral de
chamados com o nome do morador. Os filtros opcionais `estado` e `morador_id`
podem ser usados juntos. Exemplos: `/admin/chamados?estado=Aberto` e
`/admin/chamados?estado=Resolvido&morador_id=3`.

`GET /admin/chamados/contagens` retorna a quantidade total de chamados em cada
estado (`abertos`, `em_analise` e `resolvidos`) e também exige perfil
`administrador`.

## Alterar estado do chamado

A rota `PATCH /chamados/<id>/estado` exige perfil administrador e recebe o novo
estado no JSON. As transições permitidas são `Aberto` para `Em Análise` ou
`Resolvido`, e `Em Análise` para `Resolvido`. `Resolvido` é um estado final.


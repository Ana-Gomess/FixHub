# Front-end do FixHub

## Executar

As páginas são servidas pelo Flask. Para instalar as dependências e iniciar o
servidor, siga as instruções do [README do backend](../backend/README.md).
Com o servidor ativo, abra:

- Cadastro: `http://127.0.0.1:5000/cadastro`
- Login: `http://127.0.0.1:5000/login`
- Meus chamados: `http://127.0.0.1:5000/meus-chamados` (morador autenticado)

## Login

A tela em `templates/login.html` envia o e-mail e a senha em JSON para
`POST /login`. A API valida as credenciais, cria a sessão do usuário e retorna
seus dados públicos. A página mostra uma mensagem de sucesso ou o erro retornado
pela API. O botão `Mostrar` permite conferir a senha digitada.

Os estilos da tela ficam em `static/css/login.css`, que reutiliza o estilo
compartilhado do cadastro, e o comportamento do formulário fica em
`static/js/login.js`.

## Cadastro

O cadastro público cria contas de morador por meio de `POST /usuarios`. O link
`Entrar` na tela de cadastro abre a página de login. O backend não permite
escolher o perfil de administrador durante o cadastro público.

## Task #22 — Lista “Meus chamados”

A página está disponível em `/meus-chamados` e deve ser usada por um morador
autenticado. Após o login de morador, o sistema abre essa lista. O botão `Abrir
chamado` leva ao formulário em `/chamados/novo`.

O JavaScript da página consulta `GET /chamados` usando a sessão Flask atual. A
API verifica a permissão do usuário e retorna somente os chamados pertencentes
ao morador autenticado. Cada item mostra título, localização, estado atual e
identificador do chamado.

A página apresenta uma mensagem quando a lista está vazia, quando o usuário não
está autenticado (`401`) ou quando o perfil não tem acesso (`403`). Falhas de
conexão ou da API exibem uma mensagem e permitem tentar carregar a lista
novamente.

Arquivos da funcionalidade: `templates/meus_chamados.html`,
`static/js/meus_chamados.js` e `static/css/meus_chamados.css`. A rota HTML é
definida em `backend/fixhub/routes/paginas.py`; a API da lista fica em
`backend/rotas_chamados.py`.

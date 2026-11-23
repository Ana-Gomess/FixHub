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

## Meus chamados

A página `templates/meus_chamados.html` carrega os chamados de `GET /chamados`.
O backend usa a sessão do morador para retornar somente os chamados dele. A tela
exibe título, localização e estado atual, além de uma mensagem quando ainda não
há chamados ou quando a API retorna um erro. O link `Abrir chamado` leva a
`/chamados/novo`.

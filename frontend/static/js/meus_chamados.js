const estadoLista = document.getElementById("estadoLista");
const listaChamados = document.getElementById("listaChamados");
const botaoAtualizarLista = document.getElementById("botaoAtualizarLista");

function criarLink(href, texto) {
    const link = document.createElement("a");
    link.className = "link-estado";
    link.href = href;
    link.textContent = texto;
    return link;
}

const estadosConhecidos = new Map([
    ["Aberto", "aberto"],
    ["Em Análise", "em-analise"],
    ["Resolvido", "resolvido"]
]);

function criarIndicadorEstado(estado) {
    const indicador = document.createElement("span");
    const classe = estadosConhecidos.get(estado);
    const texto = classe ? estado : "Estado não disponível";

    indicador.className = `chamado-estado chamado-estado--${classe || "indisponivel"}`;
    indicador.textContent = texto;
    indicador.setAttribute("aria-label", `Estado: ${texto}`);
    return indicador;
}

function mostrarEstado(texto, tipo) {
    estadoLista.replaceChildren();
    estadoLista.className = `estado-lista estado-lista--${tipo}`;
    estadoLista.hidden = false;

    if (tipo === "carregando") {
        const indicador = document.createElement("span");
        indicador.className = "indicador-carregamento";
        indicador.setAttribute("aria-hidden", "true");
        estadoLista.append(indicador);
    }

    const mensagem = document.createElement("p");
    mensagem.textContent = texto;
    estadoLista.append(mensagem);
}

function mostrarErro(texto, { login = false, tentarNovamente = false } = {}) {
    mostrarEstado(texto, "erro");

    if (login) {
        estadoLista.append(criarLink("/login", "Entrar"));
    }

    if (tentarNovamente) {
        const botao = document.createElement("button");
        botao.className = "botao-tentar-novamente";
        botao.type = "button";
        botao.textContent = "Tentar novamente";
        botao.addEventListener("click", carregarChamados);
        estadoLista.append(botao);
    }
}

function criarItemChamado(chamado) {
    const item = document.createElement("li");
    const cartao = document.createElement("article");
    cartao.className = "chamado-card";

    const referencia = document.createElement("span");
    referencia.className = "chamado-referencia";
    referencia.textContent = `Chamado #${chamado.id}`;

    const titulo = document.createElement("h2");
    titulo.className = "chamado-titulo";
    const linkTitulo = document.createElement("a");
    linkTitulo.className = "chamado-titulo-link";
    linkTitulo.href = `/chamados/${encodeURIComponent(chamado.id)}/detalhes`;
    linkTitulo.textContent = chamado.titulo;
    titulo.append(linkTitulo);

    const localizacao = document.createElement("p");
    localizacao.className = "chamado-localizacao";
    localizacao.textContent = `Localização: ${chamado.localizacao}`;

    const descricao = document.createElement("p");
    descricao.className = "chamado-descricao";
    descricao.textContent = chamado.descricao;

    const indicadorEstado = criarIndicadorEstado(chamado.estado);
    cartao.append(referencia, titulo, indicadorEstado, localizacao, descricao);
    item.append(cartao);
    return item;
}

async function carregarChamados() {
    botaoAtualizarLista.disabled = true;
    botaoAtualizarLista.textContent = "Atualizando...";
    listaChamados.hidden = true;
    listaChamados.replaceChildren();
    mostrarEstado("Carregando seus chamados...", "carregando");

    try {
        const resposta = await fetch("/chamados", {
            credentials: "same-origin",
            headers: { Accept: "application/json" },
            cache: "no-store"
        });
        const dados = await resposta.json().catch(() => ({}));

        if (resposta.status === 401) {
            mostrarErro("Entre na sua conta para consultar seus chamados.", {
                login: true
            });
            return;
        }

        if (resposta.status === 403) {
            mostrarErro(
                dados.erro || "Seu perfil não tem permissão para consultar chamados."
            );
            return;
        }

        if (!resposta.ok) {
            mostrarErro(
                dados.erro || "Não foi possível carregar seus chamados. Tente novamente.",
                { tentarNovamente: true }
            );
            return;
        }

        if (!Array.isArray(dados.chamados)) {
            mostrarErro("Não foi possível carregar seus chamados. Tente novamente.", {
                tentarNovamente: true
            });
            return;
        }

        if (dados.chamados.length === 0) {
            mostrarEstado("Você ainda não abriu nenhum chamado.", "vazio");
            estadoLista.append(criarLink("/chamados/novo", "Abrir um chamado"));
            return;
        }

        listaChamados.append(...dados.chamados.map(criarItemChamado));
        estadoLista.hidden = true;
        listaChamados.hidden = false;
    } catch (erro) {
        mostrarErro(
            "Não foi possível se comunicar com o servidor. Verifique sua conexão e tente novamente.",
            { tentarNovamente: true }
        );
    } finally {
        botaoAtualizarLista.disabled = false;
        botaoAtualizarLista.textContent = "Atualizar chamados";
    }
}

botaoAtualizarLista.addEventListener("click", carregarChamados);
carregarChamados();

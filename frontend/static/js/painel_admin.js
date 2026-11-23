const estadoLista = document.getElementById("estadoLista");
const listaChamados = document.getElementById("listaChamados");

const estadosConhecidos = new Map([
    ["Aberto", "aberto"],
    ["Em Análise", "em-analise"],
    ["Resolvido", "resolvido"]
]);

function mostrarEstado(texto, tipo) {
    estadoLista.replaceChildren();
    estadoLista.className = `estado-lista estado-lista--${tipo}`;
    estadoLista.hidden = false;

    if (tipo === "carregando") {
        const indicador = document.createElement("span");
        indicador.className = "indicador-carregamento";
        indicador.setAttribute("aria-hidden", "true");
        estadoLista.appendChild(indicador);
    }

    const mensagem = document.createElement("p");
    mensagem.textContent = texto;
    estadoLista.appendChild(mensagem);
}

function mostrarErro(texto, tentarNovamente = false) {
    mostrarEstado(texto, "erro");

    if (tentarNovamente) {
        const botao = document.createElement("button");
        botao.className = "botao-tentar-novamente";
        botao.type = "button";
        botao.textContent = "Tentar novamente";
        botao.addEventListener("click", carregarChamados);
        estadoLista.appendChild(botao);
    }
}

function criarIndicadorEstado(estado) {
    const classe = estadosConhecidos.get(estado);
    const texto = classe ? estado : "Estado não disponível";
    const indicador = document.createElement("span");
    indicador.className = `chamado-estado chamado-estado--${classe || "indisponivel"}`;
    indicador.textContent = texto;
    indicador.setAttribute("aria-label", `Estado: ${texto}`);
    return indicador;
}

function adicionarCampo(cartao, rotulo, valor, classe = "") {
    const linha = document.createElement("p");
    if (classe) linha.className = classe;

    const nomeCampo = document.createElement("strong");
    nomeCampo.textContent = `${rotulo}: `;
    linha.append(nomeCampo, document.createTextNode(valor || "Não informado"));
    cartao.appendChild(linha);
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
    titulo.textContent = chamado.titulo || "Chamado sem título";

    const estado = criarIndicadorEstado(chamado.estado);
    cartao.append(referencia, titulo, estado);

    adicionarCampo(
        cartao,
        "Morador",
        chamado.morador_nome
            || (chamado.morador_id ? `Morador #${chamado.morador_id}` : "Não identificado"),
        "chamado-responsavel"
    );

    const localizacao = document.createElement("p");
    localizacao.className = "chamado-localizacao";
    localizacao.textContent = `Localização: ${chamado.localizacao || "Não informada"}`;

    const descricao = document.createElement("p");
    descricao.className = "chamado-descricao";
    descricao.textContent = chamado.descricao || "Descrição não informada.";

    cartao.append(localizacao, descricao);
    item.appendChild(cartao);
    return item;
}

async function carregarChamados() {
    listaChamados.hidden = true;
    listaChamados.replaceChildren();
    mostrarEstado("Carregando chamados...", "carregando");

    try {
        const resposta = await fetch("/admin/chamados", {
            headers: { Accept: "application/json" },
            credentials: "same-origin"
        });
        const dados = await resposta.json().catch(() => ({}));

        if (resposta.status === 401) {
            mostrarErro("Entre na sua conta de administrador para ver os chamados.");
            estadoLista.appendChild(criarLinkLogin());
            return;
        }

        if (resposta.status === 403) {
            mostrarErro("Seu perfil não tem permissão para acessar o painel administrativo.");
            return;
        }

        if (!resposta.ok) {
            mostrarErro(
                dados.erro || "Não foi possível carregar os chamados. Tente novamente.",
                true
            );
            return;
        }

        if (!Array.isArray(dados.chamados)) {
            mostrarErro("A resposta do servidor está inválida. Tente novamente.", true);
            return;
        }

        if (dados.chamados.length === 0) {
            mostrarEstado("Ainda não há chamados cadastrados.", "vazio");
            return;
        }

        listaChamados.append(...dados.chamados.map(criarItemChamado));
        estadoLista.hidden = true;
        listaChamados.hidden = false;
    } catch (erro) {
        mostrarErro(
            "Não foi possível se comunicar com o servidor. Verifique sua conexão e tente novamente.",
            true
        );
    }
}

function criarLinkLogin() {
    const link = document.createElement("a");
    link.className = "link-estado";
    link.href = "/login";
    link.textContent = "Entrar";
    return link;
}

carregarChamados();

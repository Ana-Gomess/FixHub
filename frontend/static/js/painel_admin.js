const estadoLista = document.getElementById("estadoLista");
const listaChamados = document.getElementById("listaChamados");
const estadoContagens = document.getElementById("estadoContagens");
const cartoesContagem = document.getElementById("cartoesContagem");
const estadoAtualizacao = document.getElementById("estadoAtualizacao");
const formFiltros = document.getElementById("formFiltros");
const filtroEstado = document.getElementById("filtroEstado");
const filtroMorador = document.getElementById("filtroMorador");
const estadoMoradores = document.getElementById("estadoMoradores");
const botaoTentarMoradores = document.getElementById("botaoTentarMoradores");

const estadosConhecidos = new Map([
    ["Aberto", "aberto"],
    ["Em Análise", "em-analise"],
    ["Resolvido", "resolvido"]
]);

const proximosEstados = new Map([
    ["Aberto", ["Em Análise", "Resolvido"]],
    ["Em Análise", ["Resolvido"]],
    ["Resolvido", []]
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
    cartao.appendChild(criarControlesEstado(chamado));
    item.appendChild(cartao);
    return item;
}

function criarControlesEstado(chamado) {
    const formulario = document.createElement("form");
    formulario.className = "controles-estado";

    const rotulo = document.createElement("label");
    rotulo.className = "rotulo-seletor-estado";
    rotulo.htmlFor = `novo-estado-${chamado.id}`;
    rotulo.textContent = "Alterar estado";

    const seletor = document.createElement("select");
    seletor.id = `novo-estado-${chamado.id}`;
    seletor.name = "estado";
    seletor.className = "seletor-estado-chamado";
    seletor.required = true;

    const estadosPermitidos = proximosEstados.get(chamado.estado) || [];
    const opcaoInicial = document.createElement("option");
    opcaoInicial.value = "";
    opcaoInicial.textContent = estadosPermitidos.length
        ? "Selecione o novo estado"
        : "Sem novas transições";
    seletor.appendChild(opcaoInicial);

    estadosPermitidos.forEach((estado) => {
        const opcao = document.createElement("option");
        opcao.value = estado;
        opcao.textContent = estado;
        seletor.appendChild(opcao);
    });

    const botao = document.createElement("button");
    botao.className = "botao-salvar-estado";
    botao.type = "submit";
    botao.textContent = "Salvar estado";
    botao.disabled = estadosPermitidos.length === 0;

    const feedback = document.createElement("p");
    feedback.className = "feedback-estado-chamado";
    feedback.setAttribute("role", "status");
    feedback.setAttribute("aria-live", "polite");

    seletor.addEventListener("change", () => {
        botao.disabled = !seletor.value;
    });
    formulario.addEventListener("submit", (evento) => {
        evento.preventDefault();
        if (seletor.value) atualizarEstadoChamado(chamado.id, seletor.value, formulario);
    });

    formulario.append(rotulo, seletor, botao, feedback);
    return formulario;
}

function mostrarEstadoAtualizacao(texto, tipo = "sucesso") {
    estadoAtualizacao.textContent = texto;
    estadoAtualizacao.className = `estado-atualizacao estado-atualizacao--${tipo}`;
    estadoAtualizacao.hidden = !texto;
}

async function atualizarEstadoChamado(chamadoId, novoEstado, formulario) {
    const seletor = formulario.elements.estado;
    const botao = formulario.querySelector("button[type='submit']");
    const feedback = formulario.querySelector(".feedback-estado-chamado");
    botao.disabled = true;
    seletor.disabled = true;
    feedback.textContent = "Salvando alteração...";
    feedback.className = "feedback-estado-chamado";

    try {
        const resposta = await fetch(`/chamados/${chamadoId}/estado`, {
            method: "PATCH",
            headers: {
                Accept: "application/json",
                "Content-Type": "application/json"
            },
            credentials: "same-origin",
            body: JSON.stringify({ estado: novoEstado })
        });
        const dados = await resposta.json().catch(() => ({}));

        if (!resposta.ok) {
            const mensagem = resposta.status === 401
                ? "Sua sessão expirou. Entre novamente para alterar o estado."
                : resposta.status === 403
                    ? "Seu perfil não tem permissão para alterar estados."
                    : dados.erro || "Não foi possível alterar o estado do chamado.";
            feedback.textContent = mensagem;
            feedback.classList.add("feedback-estado-chamado--erro");
            return;
        }

        mostrarEstadoAtualizacao(dados.mensagem || "Estado atualizado com sucesso.");
        await Promise.all([carregarChamados(), carregarContagens()]);
    } catch (erro) {
        feedback.textContent = "Não foi possível se comunicar com o servidor. Tente novamente.";
        feedback.classList.add("feedback-estado-chamado--erro");
    } finally {
        seletor.disabled = false;
        botao.disabled = !seletor.value;
    }
}

async function carregarChamados() {
    listaChamados.hidden = true;
    listaChamados.replaceChildren();
    mostrarEstado("Carregando chamados...", "carregando");

    try {
        const parametros = new URLSearchParams();
        if (filtroEstado.value) parametros.set("estado", filtroEstado.value);
        if (filtroMorador.value) parametros.set("morador_id", filtroMorador.value);
        const query = parametros.toString();
        const resposta = await fetch(`/admin/chamados${query ? `?${query}` : ""}`, {
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
            const filtrosAtivos = Boolean(filtroEstado.value || filtroMorador.value);
            mostrarEstado(
                filtrosAtivos
                    ? "Nenhum chamado corresponde aos filtros selecionados."
                    : "Ainda não há chamados cadastrados.",
                "vazio"
            );
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

function mostrarEstadoMoradores(texto = "", tipo = "") {
    estadoMoradores.textContent = texto;
    estadoMoradores.className = tipo ? `estado-moradores estado-moradores--${tipo}` : "estado-moradores";
    estadoMoradores.hidden = !texto;
}

async function carregarMoradores() {
    filtroMorador.disabled = true;
    botaoTentarMoradores.hidden = true;
    mostrarEstadoMoradores("Carregando moradores...", "carregando");

    try {
        const resposta = await fetch("/admin/moradores", {
            headers: { Accept: "application/json" },
            credentials: "same-origin"
        });
        const dados = await resposta.json().catch(() => ({}));

        if (resposta.status === 401) {
            mostrarEstadoMoradores("Entre como administrador para carregar os moradores.", "erro");
            return;
        }
        if (resposta.status === 403) {
            mostrarEstadoMoradores("Seu perfil não tem permissão para listar moradores.", "erro");
            return;
        }
        if (!resposta.ok || !Array.isArray(dados.moradores)) {
            mostrarEstadoMoradores(dados.erro || "Não foi possível carregar os moradores.", "erro");
            botaoTentarMoradores.hidden = false;
            return;
        }

        filtroMorador.replaceChildren(new Option("Todos os moradores", ""));
        dados.moradores.forEach((morador) => {
            if (morador && Number.isInteger(morador.id) && typeof morador.nome === "string") {
                filtroMorador.add(new Option(morador.nome, String(morador.id)));
            }
        });
        filtroMorador.disabled = false;
        mostrarEstadoMoradores();
    } catch (erro) {
        mostrarEstadoMoradores("Não foi possível se comunicar com o servidor para carregar os moradores.", "erro");
        botaoTentarMoradores.hidden = false;
    }
}

function criarLinkLogin() {
    const link = document.createElement("a");
    link.className = "link-estado";
    link.href = "/login";
    link.textContent = "Entrar";
    return link;
}

function mostrarEstadoContagens(texto, tipo, tentarNovamente = false) {
    estadoContagens.replaceChildren();
    estadoContagens.className = `estado-lista estado-lista--${tipo}`;
    estadoContagens.hidden = false;
    cartoesContagem.hidden = true;

    const mensagem = document.createElement("p");
    mensagem.textContent = texto;
    estadoContagens.appendChild(mensagem);

    if (tipo === "carregando") {
        const indicador = document.createElement("span");
        indicador.className = "indicador-carregamento";
        indicador.setAttribute("aria-hidden", "true");
        estadoContagens.prepend(indicador);
    }

    if (tentarNovamente) {
        const botao = document.createElement("button");
        botao.className = "botao-tentar-novamente";
        botao.type = "button";
        botao.textContent = "Tentar novamente";
        botao.addEventListener("click", carregarContagens);
        estadoContagens.appendChild(botao);
    }
}

async function carregarContagens() {
    mostrarEstadoContagens("Carregando contagens...", "carregando");

    try {
        const resposta = await fetch("/admin/chamados/contagens", {
            headers: { Accept: "application/json" },
            credentials: "same-origin"
        });
        const dados = await resposta.json().catch(() => ({}));

        if (resposta.status === 401) {
            mostrarEstadoContagens(
                "Entre na sua conta de administrador para ver as contagens.",
                "erro"
            );
            estadoContagens.appendChild(criarLinkLogin());
            return;
        }

        if (!resposta.ok) {
            mostrarEstadoContagens(
                dados.erro || "Não foi possível carregar as contagens.",
                "erro",
                resposta.status !== 403
            );
            return;
        }

        const contagens = dados.contagens;
        const valores = [
            contagens?.abertos,
            contagens?.em_analise,
            contagens?.resolvidos
        ];
        if (!valores.every((valor) => Number.isInteger(valor) && valor >= 0)) {
            mostrarEstadoContagens(
                "A resposta de contagens está inválida. Tente novamente.",
                "erro",
                true
            );
            return;
        }

        const formatador = new Intl.NumberFormat("pt-BR");
        document.getElementById("contagemAbertos").textContent = formatador.format(contagens.abertos);
        document.getElementById("contagemEmAnalise").textContent = formatador.format(contagens.em_analise);
        document.getElementById("contagemResolvidos").textContent = formatador.format(contagens.resolvidos);

        estadoContagens.hidden = true;
        cartoesContagem.hidden = false;
    } catch (erro) {
        mostrarEstadoContagens(
            "Não foi possível se comunicar com o servidor. Verifique sua conexão e tente novamente.",
            "erro",
            true
        );
    }
}

formFiltros.addEventListener("submit", (evento) => {
    evento.preventDefault();
    carregarChamados();
});

document.getElementById("botaoLimparFiltros").addEventListener("click", () => {
    formFiltros.reset();
    carregarChamados();
});

botaoTentarMoradores.addEventListener("click", carregarMoradores);

carregarMoradores();
carregarContagens();
carregarChamados();

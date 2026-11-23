const mensagemLista = document.getElementById("mensagemLista");
const listaChamados = document.getElementById("listaChamados");
const botaoTentarNovamente = document.getElementById("botaoTentarNovamente");

botaoTentarNovamente.addEventListener("click", carregarChamados);

carregarChamados();

async function carregarChamados() {
    mensagemLista.textContent = "Carregando seus chamados...";
    mensagemLista.className = "mensagem-lista";
    listaChamados.replaceChildren();
    botaoTentarNovamente.hidden = true;

    try {
        const resposta = await fetch("/chamados", {
            method: "GET",
            credentials: "same-origin",
            headers: { "Accept": "application/json" }
        });
        const dados = await resposta.json().catch(() => ({}));

        if (!resposta.ok) {
            if (resposta.status === 401) {
                throw new Error("Faça login para consultar seus chamados.");
            }
            if (resposta.status === 403) {
                throw new Error("Esta lista está disponível para moradores.");
            }
            throw new Error(
                dados.erro || "Não foi possível carregar seus chamados."
            );
        }

        const chamados = Array.isArray(dados.chamados) ? dados.chamados : [];
        if (chamados.length === 0) {
            mensagemLista.textContent = "Você ainda não abriu chamados.";
            mensagemLista.className = "mensagem-lista estado-vazio";
            return;
        }

        mensagemLista.textContent = `${chamados.length} ${chamados.length === 1 ? "chamado encontrado" : "chamados encontrados"}.`;
        mensagemLista.className = "mensagem-lista mensagem-sucesso";
        chamados.forEach((chamado) => {
            listaChamados.appendChild(criarCartaoChamado(chamado));
        });
    } catch (erro) {
        mensagemLista.textContent = erro.message || "Erro de conexão com o servidor.";
        mensagemLista.className = "mensagem-lista mensagem-erro";
        botaoTentarNovamente.hidden = false;
    }
}

function criarCartaoChamado(chamado) {
    const cartao = document.createElement("article");
    cartao.className = "item-chamado";

    const cabecalho = document.createElement("div");
    cabecalho.className = "item-cabecalho";

    const titulo = document.createElement("h2");
    titulo.textContent = chamado.titulo || "Chamado sem título";
    cabecalho.appendChild(titulo);

    const estado = document.createElement("span");
    estado.className = `estado estado-${classeEstado(chamado.estado)}`;
    estado.textContent = chamado.estado || "Estado indisponível";
    cabecalho.appendChild(estado);
    cartao.appendChild(cabecalho);

    const localizacao = document.createElement("p");
    localizacao.className = "item-localizacao";
    localizacao.textContent = `Localização: ${chamado.localizacao || "Não informada"}`;
    cartao.appendChild(localizacao);

    if (chamado.id !== undefined && chamado.id !== null) {
        const identificador = document.createElement("p");
        identificador.className = "item-identificador";
        identificador.textContent = `Chamado #${chamado.id}`;
        cartao.appendChild(identificador);
    }

    return cartao;
}

function classeEstado(estado) {
    const classes = {
        "Aberto": "aberto",
        "Em Análise": "em-analise",
        "Resolvido": "resolvido"
    };
    return classes[estado] || "desconhecido";
}

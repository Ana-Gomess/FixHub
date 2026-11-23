const paginaDetalhe = document.getElementById("detalheChamado");
const estadoDetalhe = document.getElementById("estadoDetalhe");
const conteudoDetalhe = document.getElementById("conteudoDetalhe");
const botaoAtualizarDetalhe = document.getElementById("botaoAtualizarDetalhe");
const estadosConhecidos = new Map([
    ["Aberto", "aberto"],
    ["Em Análise", "em-analise"],
    ["Resolvido", "resolvido"]
]);

function criarLink(href, texto) {
    const link = document.createElement("a");
    link.href = href;
    link.textContent = texto;
    return link;
}

function mostrarEstado(texto, tipo = "erro", acoes = []) {
    conteudoDetalhe.hidden = true;
    estadoDetalhe.replaceChildren();
    estadoDetalhe.className = `estado-detalhe estado-detalhe--${tipo}`;
    estadoDetalhe.hidden = false;

    if (tipo === "carregando") {
        const indicadorCarregamento = document.createElement("span");
        indicadorCarregamento.className = "indicador-carregamento";
        indicadorCarregamento.setAttribute("aria-hidden", "true");
        estadoDetalhe.append(indicadorCarregamento);
    }
    const mensagem = document.createElement("p");
    mensagem.textContent = texto;
    estadoDetalhe.append(mensagem, ...acoes);
}

function mostrarErro(texto, { login = false, tentarNovamente = false } = {}) {
    const acoes = [];
    if (login) {
        acoes.push(criarLink("/login", "Entrar"));
    }
    acoes.push(criarLink("/meus-chamados", "Voltar para meus chamados"));

    if (tentarNovamente) {
        const botao = document.createElement("button");
        botao.className = "botao-tentar-novamente";
        botao.type = "button";
        botao.textContent = "Tentar novamente";
        botao.addEventListener("click", carregarDetalhe);
        acoes.push(botao);
    }

    mostrarEstado(texto, "erro", acoes);
}

function textoOuIndisponivel(valor) {
    return typeof valor === "string" && valor.trim()
        ? valor
        : "Não informado";
}

function preencherDetalhe(chamado) {
    document.getElementById("referenciaChamado").textContent = `Chamado #${chamado.id}`;
    document.getElementById("tituloChamado").textContent = textoOuIndisponivel(chamado.titulo);
    document.getElementById("descricaoChamado").textContent = textoOuIndisponivel(chamado.descricao);
    document.getElementById("localizacaoChamado").textContent = textoOuIndisponivel(chamado.localizacao);

    const indicador = document.getElementById("estadoChamado");
    const classe = estadosConhecidos.get(chamado.estado);
    const estado = classe ? chamado.estado : "Estado não disponível";
    indicador.className = `chamado-estado chamado-estado--${classe || "indisponivel"}`;
    indicador.textContent = estado;
    indicador.setAttribute("aria-label", `Estado: ${estado}`);

    estadoDetalhe.hidden = true;
    conteudoDetalhe.hidden = false;
}

async function carregarDetalhe() {
    botaoAtualizarDetalhe.disabled = true;
    botaoAtualizarDetalhe.textContent = "Atualizando...";
    mostrarEstado("Carregando os detalhes do chamado...", "carregando");
    const chamadoId = paginaDetalhe.dataset.chamadoId;

    try {
        const resposta = await fetch(`/chamados/${encodeURIComponent(chamadoId)}`, {
            credentials: "same-origin",
            headers: { Accept: "application/json" },
            cache: "no-store"
        });
        const dados = await resposta.json().catch(() => ({}));

        if (resposta.status === 401) {
            mostrarErro("Entre na sua conta para consultar este chamado.", { login: true });
            return;
        }

        if (resposta.status === 404 || resposta.status === 403) {
            mostrarErro("Este chamado não foi encontrado ou não está disponível para sua conta.");
            return;
        }

        if (!resposta.ok) {
            mostrarErro(
                dados.erro || "Não foi possível carregar os detalhes do chamado.",
                { tentarNovamente: true }
            );
            return;
        }

        if (!dados.chamado || typeof dados.chamado !== "object") {
            mostrarErro("Não foi possível carregar os detalhes do chamado.", {
                tentarNovamente: true
            });
            return;
        }

        preencherDetalhe(dados.chamado);
    } catch (erro) {
        mostrarErro(
            "Não foi possível se comunicar com o servidor. Verifique sua conexão e tente novamente.",
            { tentarNovamente: true }
        );
    } finally {
        botaoAtualizarDetalhe.disabled = false;
        botaoAtualizarDetalhe.textContent = "Atualizar estado";
    }
}

botaoAtualizarDetalhe.addEventListener("click", carregarDetalhe);
carregarDetalhe();

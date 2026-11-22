const listaChamados = document.getElementById("listaChamados");

function criarCartaoChamado(chamado) {
    const cartao = document.createElement("article");
    cartao.className = "chamado-item";

    const cabecalho = document.createElement("div");
    cabecalho.className = "chamado-item-cabecalho";

    const titulo = document.createElement("h2");
    titulo.textContent = chamado.titulo;

    const estado = document.createElement("span");
    estado.className = "estado-chamado";
    estado.textContent = chamado.estado;

    cabecalho.append(titulo, estado);
    cartao.append(cabecalho);

    for (const [rotulo, valor] of [
        ["Descrição", chamado.descricao],
        ["Localização", chamado.localizacao]
    ]) {
        const linha = document.createElement("p");
        const texto = document.createElement("strong");
        texto.textContent = `${rotulo}: `;
        linha.append(texto, document.createTextNode(valor));
        cartao.append(linha);
    }

    return cartao;
}

async function carregarMeusChamados() {
    try {
        const resposta = await fetch("/chamados", {
            method: "GET",
            credentials: "same-origin"
        });
        const dados = await resposta.json().catch(() => ({}));

        if (resposta.status === 401) {
            window.location.replace("/login");
            return;
        }

        if (!resposta.ok) {
            console.error(dados.erro || "Não foi possível carregar os chamados.");
            listaChamados.replaceChildren();
            return;
        }

        const chamados = Array.isArray(dados.chamados) ? dados.chamados : [];
        if (chamados.length === 0) {
            const vazio = document.createElement("p");
            vazio.className = "estado-vazio";
            vazio.textContent = "Você ainda não abriu chamados.";
            listaChamados.replaceChildren(vazio);
            return;
        }

        listaChamados.replaceChildren(...chamados.map(criarCartaoChamado));
    } catch (erro) {
        console.error("Erro ao carregar os chamados:", erro);
        listaChamados.replaceChildren();
    }
}

carregarMeusChamados();

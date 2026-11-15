const listaChamados = document.getElementById("listaChamados");
const mensagem = document.getElementById("mensagem");
const botaoAtualizar = document.getElementById("botaoAtualizar");

// Estados que podem ser escolhidos a partir do estado atual.
const transicoesPermitidas = {
    "Aberto": ["Em Análise", "Resolvido"],
    "Em Análise": ["Resolvido"],
    "Resolvido": []
};

// Exibe mensagens na tela.
function mostrarMensagem(texto, tipo) {
    mensagem.textContent = texto;
    mensagem.className = tipo;
}

// Evita interpretar os dados recebidos da API como HTML.
function escaparHTML(valor) {
    return String(valor ?? "").replace(/[&<>"']/g, caractere => {
        const caracteres = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        };

        return caracteres[caractere];
    });
}

// Cria o seletor de estado de cada chamado.
function criarSeletorEstado(chamado) {
    const seletor = document.createElement("select");

    seletor.className = "seletor-estado";
    seletor.setAttribute("aria-label", `Estado do chamado ${chamado.id}`);

    const estadosDisponiveis = [
        chamado.estado,
        ...transicoesPermitidas[chamado.estado]
    ];

    estadosDisponiveis.forEach(estado => {
        const opcao = document.createElement("option");

        opcao.value = estado;
        opcao.textContent = estado;

        if (estado === chamado.estado) {
            opcao.selected = true;
        }

        seletor.appendChild(opcao);
    });

    if (chamado.estado === "Resolvido") {
        seletor.disabled = true;
    }

    seletor.addEventListener("change", async () => {
        const estadoAnterior = chamado.estado;
        const novoEstado = seletor.value;

        seletor.disabled = true;

        try {
            const resposta = await fetch(
                `/chamados/${chamado.id}/estado`,
                {
                    method: "PATCH",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    credentials: "same-origin",
                    body: JSON.stringify({
                        estado: novoEstado
                    })
                }
            );

            const dados = await resposta.json();

            if (resposta.status === 401) {
                window.location.href = "/login";
                return;
            }

            if (!resposta.ok) {
                throw new Error(
                    dados.erro || "Não foi possível alterar o estado."
                );
            }

            chamado.estado = dados.chamado.estado;

            mostrarMensagem(
                dados.mensagem || "Estado atualizado com sucesso!",
                "mensagem-sucesso"
            );

            // Atualiza o seletor conforme o novo estado.
            await carregarChamados();

        } catch (erro) {
            chamado.estado = estadoAnterior;

            seletor.value = estadoAnterior;

            mostrarMensagem(
                erro.message,
                "mensagem-erro"
            );

            seletor.disabled = estadoAnterior === "Resolvido";
        }
    });

    return seletor;
}

// Cria o cartão visual de cada chamado.
function criarCartaoChamado(chamado) {
    const cartao = document.createElement("article");

    cartao.className = "chamado-card";

    cartao.innerHTML = `
        <div class="chamado-topo">
            <div>
                <h3>${escaparHTML(chamado.titulo)}</h3>
                <span class="chamado-id">
                    Chamado #${escaparHTML(chamado.id)}
                </span>
            </div>
        </div>

        <p class="chamado-descricao">
            ${escaparHTML(chamado.descricao)}
        </p>

        <div class="chamado-informacoes">
            <span>
                Localização: ${escaparHTML(chamado.localizacao)}
            </span>

            <span>
                Morador: ${escaparHTML(chamado.morador_nome)}
            </span>
        </div>

        <div class="controle-estado">
            <label>Estado do chamado</label>
        </div>
    `;

    const controle = cartao.querySelector(".controle-estado");

    controle.appendChild(criarSeletorEstado(chamado));

    return cartao;
}

// Busca os chamados registrados no backend.
async function carregarChamados() {
    listaChamados.innerHTML = `
        <div class="carregando">Carregando chamados...</div>
    `;

    botaoAtualizar.disabled = true;

    try {
        const resposta = await fetch("/admin/chamados", {
            method: "GET",
            credentials: "same-origin"
        });

        const dados = await resposta.json();

        if (resposta.status === 401) {
            window.location.href = "/login";
            return;
        }

        if (resposta.status === 403) {
            mostrarMensagem(
                "Você não tem permissão para acessar o painel administrativo.",
                "mensagem-erro"
            );

            listaChamados.innerHTML = "";
            return;
        }

        if (!resposta.ok) {
            throw new Error(
                dados.erro || "Não foi possível carregar os chamados."
            );
        }

        listaChamados.innerHTML = "";

        if (dados.chamados.length === 0) {
            listaChamados.innerHTML = `
                <div class="sem-chamados">
                    Nenhum chamado foi registrado ainda.
                </div>
            `;

            return;
        }

        dados.chamados.forEach(chamado => {
            const cartao = criarCartaoChamado(chamado);
            listaChamados.appendChild(cartao);
        });

    } catch (erro) {
        listaChamados.innerHTML = "";

        mostrarMensagem(
            erro.message || "Erro ao carregar os chamados.",
            "mensagem-erro"
        );

    } finally {
        botaoAtualizar.disabled = false;
    }
}

// Botão para atualizar a listagem.
botaoAtualizar.addEventListener("click", () => {
    mostrarMensagem("", "");
    carregarChamados();
});

// Carrega os chamados ao abrir a página.
carregarChamados();
const botaoSair = document.getElementById("botaoSair");

botaoSair.addEventListener("click", async () => {
    try {
        const resposta = await fetch("/logout", {
            method: "POST",
            credentials: "same-origin"
        });

        if (!resposta.ok) {
            throw new Error("Não foi possível sair da conta.");
        }

        window.location.href = "/login";

    } catch (erro) {
        alert(erro.message);
    }
});
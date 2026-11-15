
const formulario = document.getElementById("formChamado");
const mensagem = document.getElementById("mensagem");
const botaoChamado = document.getElementById("botaoChamado");

// Enviar chamado para o backend
formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();

    mensagem.textContent = "";
    mensagem.className = "";

    const titulo = document.getElementById("titulo").value.trim();
    const descricao = document.getElementById("descricao").value.trim();
    const localizacao = document.getElementById("localizacao").value.trim();

    // Validar campos
    if (!titulo || !descricao || !localizacao) {
        mostrarMensagem("Preencha todos os campos.", "erro");
        return;
    }

    botaoChamado.disabled = true;
    botaoChamado.textContent = "Enviando chamado...";

    try {
        const resposta = await fetch("/chamados", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "same-origin",
            body: JSON.stringify({
                titulo: titulo,
                descricao: descricao,
                localizacao: localizacao
            })
        });

        const dados = await resposta.json().catch(() => ({}));

        if (!resposta.ok) {
            throw new Error(
                dados.mensagem ||
                dados.erro ||
                "Não foi possível abrir o chamado."
            );
        }

        mostrarMensagem(
            "Chamado aberto com sucesso!",
            "sucesso"
        );

        formulario.reset();

        await carregarMeusChamados();

    } catch (erro) {
        mostrarMensagem(
            erro.message || "Erro ao conectar com o servidor.",
            "erro"
        );

    } finally {
        botaoChamado.disabled = false;
        botaoChamado.textContent = "Enviar chamado";
    }
});

// Exibir mensagens de erro ou confirmação
function mostrarMensagem(texto, tipo) {
    mensagem.textContent = texto;

    mensagem.className = tipo === "sucesso"
        ? "mensagem-sucesso"
        : "mensagem-erro";
}

// BOTÃO SAIR DA CONTA

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


// LISTAR CHAMADOS DO MORADOR

const listaMeusChamados = document.getElementById("listaMeusChamados");
const mensagemChamados = document.getElementById("mensagemChamados");
const botaoAtualizarChamados = document.getElementById("botaoAtualizarChamados");

// Evitar problemas ao exibir textos recebidos do backend
function escaparHTML(texto) {
    return String(texto).replace(/[&<>"']/g, (caractere) => {
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

// Criar o cartão de cada chamado
function criarCartaoMorador(chamado) {

    let classeEstado = "";

    if (chamado.estado === "Aberto") {
        classeEstado = "estado-aberto";
    } else if (chamado.estado === "Em Análise") {
        classeEstado = "estado-em-analise";
    } else if (chamado.estado === "Resolvido") {
        classeEstado = "estado-resolvido";
    }

    return `
        <article class="meu-chamado">

            <div class="chamado-cabecalho">

                <h3>${escaparHTML(chamado.titulo)}</h3>

                <span class="estado-badge ${classeEstado}">
                    ${escaparHTML(chamado.estado)}
                </span>

            </div>

            <p>
                <strong>Chamado:</strong> #${escaparHTML(chamado.id)}
            </p>

            <p>
                <strong>Descrição:</strong>
                ${escaparHTML(chamado.descricao)}
            </p>

            <p>
                <strong>Localização:</strong>
                ${escaparHTML(chamado.localizacao)}
            </p>

        </article>
    `;
}

// Buscar chamados no backend
async function carregarMeusChamados() {

    mensagemChamados.textContent = "";
    botaoAtualizarChamados.disabled = true;
    botaoAtualizarChamados.textContent = "Atualizando...";

    try {

        const resposta = await fetch("/chamados", {
            method: "GET",
            credentials: "same-origin"
        });

        const dados = await resposta.json().catch(() => ({}));

        if (resposta.status === 401) {
            window.location.href = "/login";
            return;
        }

        if (!resposta.ok) {
            throw new Error(
                dados.erro || "Não foi possível carregar seus chamados."
            );
        }

        const chamados = dados.chamados || [];

        if (chamados.length === 0) {

            listaMeusChamados.innerHTML = `
                <p class="sem-chamados">
                    Você ainda não possui chamados abertos.
                </p>
            `;

            return;
        }

        listaMeusChamados.innerHTML = `
            <div class="lista-meus-chamados">
                ${chamados.map(criarCartaoMorador).join("")}
            </div>
        `;

    } catch (erro) {

        mensagemChamados.textContent =
            erro.message || "Erro ao carregar chamados.";

    } finally {

        botaoAtualizarChamados.disabled = false;
        botaoAtualizarChamados.textContent = "Atualizar";
    }
}

// Botão para atualizar a lista manualmente
botaoAtualizarChamados.addEventListener("click", carregarMeusChamados);

// Carregar chamados quando a página abrir
carregarMeusChamados();

// Consultar atualizações automaticamente a cada 15 segundos
setInterval(carregarMeusChamados, 15000);
const formulario = document.getElementById("formCadastro");
const mensagem = document.getElementById("mensagem");
const botaoCadastro = document.getElementById("botaoCadastro");
const campoSenha = document.getElementById("senha");
const campoBloco = document.getElementById("bloco");
const botaoMostrarSenha = document.getElementById("mostrarSenha");

let blocosCarregados = false;
botaoCadastro.disabled = true;

botaoMostrarSenha.addEventListener("click", () => {
    const senhaEstaOculta = campoSenha.type === "password";
    campoSenha.type = senhaEstaOculta ? "text" : "password";
    botaoMostrarSenha.textContent = senhaEstaOculta ? "Ocultar" : "Mostrar";
});

async function carregarBlocos() {
    try {
        const resposta = await fetch("/blocos");
        const dados = await resposta.json().catch(() => ({}));

        if (!resposta.ok || !Array.isArray(dados.blocos) || !dados.blocos.length) {
            throw new Error("Não foi possível carregar os blocos.");
        }

        const opcaoInicial = document.createElement("option");
        opcaoInicial.value = "";
        opcaoInicial.textContent = "Selecione o bloco";
        campoBloco.replaceChildren(opcaoInicial);

        for (const bloco of dados.blocos) {
            const opcao = document.createElement("option");
            opcao.value = bloco;
            opcao.textContent = `Bloco ${bloco}`;
            campoBloco.appendChild(opcao);
        }

        campoBloco.disabled = false;
        blocosCarregados = true;
        botaoCadastro.disabled = false;
    } catch (erro) {
        const opcaoErro = document.createElement("option");
        opcaoErro.value = "";
        opcaoErro.textContent = "Blocos indisponíveis";
        campoBloco.replaceChildren(opcaoErro);
        mostrarMensagem(
            erro.message || "Não foi possível carregar a lista de blocos. Atualize a página.",
            "erro"
        );
    }
}

carregarBlocos();

formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    mensagem.textContent = "";
    mensagem.className = "";

    const nome = document.getElementById("nome").value.trim();
    const email = document.getElementById("email").value.trim();
    const senha = campoSenha.value;
    const bloco = campoBloco.value;

    if (!blocosCarregados) {
        mostrarMensagem("A lista de blocos ainda não está disponível.", "erro");
        return;
    }

    if (!nome || !email || !senha || !bloco) {
        mostrarMensagem("Preencha todos os campos e selecione um bloco.", "erro");
        return;
    }

    botaoCadastro.disabled = true;
    botaoCadastro.textContent = "Criando conta...";

    try {
        const resposta = await fetch("/usuarios", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ nome, email, senha, bloco })
        });

        const dados = await resposta.json().catch(() => ({}));

        if (!resposta.ok) {
            throw new Error(
                dados.mensagem ||
                dados.erro ||
                "Não foi possível realizar o cadastro."
            );
        }

        mostrarMensagem("Conta criada com sucesso.", "sucesso");
        formulario.reset();
    } catch (erro) {
        mostrarMensagem(
            erro.message || "Erro de conexão com o servidor.",
            "erro"
        );
    } finally {
        botaoCadastro.disabled = !blocosCarregados;
        botaoCadastro.textContent = "Criar conta";
    }
});

function mostrarMensagem(texto, tipo) {
    mensagem.textContent = texto;
    mensagem.className = tipo === "sucesso"
        ? "mensagem-sucesso"
        : "mensagem-erro";
}

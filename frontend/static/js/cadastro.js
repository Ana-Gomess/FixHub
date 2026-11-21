const formulario = document.getElementById("formCadastro");
const mensagem = document.getElementById("mensagem");
const botaoCadastro = document.getElementById("botaoCadastro");

const campoSenha = document.getElementById("senha");
const botaoMostrarSenha = document.getElementById("mostrarSenha");

// Mostrar ou esconder a senha
botaoMostrarSenha.addEventListener("click", () => {
    const senhaEstaOculta = campoSenha.type === "password";

    campoSenha.type = senhaEstaOculta ? "text" : "password";

    botaoMostrarSenha.textContent = senhaEstaOculta
        ? "Ocultar"
        : "Mostrar";
});

// Enviar cadastro para o backend
formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();

    mensagem.textContent = "";
    mensagem.className = "";

    const nome = document.getElementById("nome").value.trim();
    const email = document.getElementById("email").value.trim();
    const senha = campoSenha.value;

    if (!nome || !email || !senha) {
        mostrarMensagem("Preencha todos os campos.", "erro");
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
            body: JSON.stringify({
                nome: nome,
                email: email,
                senha: senha
            })
        });

        const dados = await resposta.json().catch(() => ({}));

        if (!resposta.ok) {
            throw new Error(
                dados.mensagem ||
                dados.erro ||
                "Não foi possível realizar o cadastro."
            );
        }

        mostrarMensagem(
            "Conta criada com sucesso! Redirecionando...",
            "sucesso"
        );

        formulario.reset();

        setTimeout(() => {
            window.location.href = "/login";
        }, 1500);

    } catch (erro) {
        mostrarMensagem(
            erro.message || "Erro de conexão com o servidor.",
            "erro"
        );

    } finally {
        botaoCadastro.disabled = false;
        botaoCadastro.textContent = "Criar conta";
    }
});

function mostrarMensagem(texto, tipo) {
    mensagem.textContent = texto;
    mensagem.className = tipo === "sucesso"
        ? "mensagem-sucesso"
        : "mensagem-erro";
}
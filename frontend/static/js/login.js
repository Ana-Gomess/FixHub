const formulario = document.getElementById("formLogin");
const mensagem = document.getElementById("mensagem");
const botaoLogin = document.getElementById("botaoLogin");

const campoSenha = document.getElementById("senha");
const botaoMostrarSenha = document.getElementById("mostrarSenha");

// Mostrar ou esconder senha
botaoMostrarSenha.addEventListener("click", () => {
    const senhaEstaOculta = campoSenha.type === "password";

    campoSenha.type = senhaEstaOculta ? "text" : "password";

    botaoMostrarSenha.textContent = senhaEstaOculta
        ? "Ocultar"
        : "Mostrar";
});

// Realizar login
formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();

    mensagem.textContent = "";
    mensagem.className = "";

    const email = document.getElementById("email").value.trim();
    const senha = campoSenha.value;

    if (!email || !senha) {
        mostrarMensagem("Preencha todos os campos.", "erro");
        return;
    }

    botaoLogin.disabled = true;
    botaoLogin.textContent = "Entrando...";

    try {
        const resposta = await fetch("/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            credentials: "same-origin",
            body: JSON.stringify({
                email: email,
                senha: senha
            })
        });

        const dados = await resposta.json().catch(() => ({}));

        if (!resposta.ok) {
            throw new Error(
                dados.mensagem ||
                dados.erro ||
                "E-mail ou senha incorretos."
            );
        }

        mostrarMensagem("Login realizado com sucesso!", "sucesso");


setTimeout(() => {
    const perfil = dados.usuario.perfil;

    if (perfil === "administrador") {
        window.location.href = "/admin";
    } else if (perfil === "morador") {
        window.location.href = "/chamado/novo";
    } else {
        mostrarMensagem("Perfil de usuário não reconhecido.", "erro");
    }
}, 1000);
     // Por enquanto, apenas confirma o login.
// Depois criaremos os painéis de morador e administrador.

    } catch (erro) {
        mostrarMensagem(
            erro.message || "Erro ao conectar com o servidor.",
            "erro"
        );

    } finally {
        botaoLogin.disabled = false;
        botaoLogin.textContent = "Entrar na conta";
    }
});

function mostrarMensagem(texto, tipo) {
    mensagem.textContent = texto;

    mensagem.className = tipo === "sucesso"
        ? "mensagem-sucesso"
        : "mensagem-erro";
}
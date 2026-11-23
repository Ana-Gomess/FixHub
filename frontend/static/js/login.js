const formulario = document.getElementById("formLogin");
const mensagem = document.getElementById("mensagem");
const botaoLogin = document.getElementById("botaoLogin");
const campoSenha = document.getElementById("senha");
const botaoMostrarSenha = document.getElementById("mostrarSenha");

botaoMostrarSenha.addEventListener("click", () => {
    const mostrar = campoSenha.type === "password";
    campoSenha.type = mostrar ? "text" : "password";
    botaoMostrarSenha.textContent = mostrar ? "Ocultar" : "Mostrar";
    botaoMostrarSenha.setAttribute("aria-pressed", String(mostrar));
});

formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    mensagem.textContent = "";
    mensagem.className = "";

    const email = document.getElementById("email").value.trim();
    const senha = campoSenha.value;

    if (!email || !senha.trim()) {
        mostrarMensagem("Informe seu e-mail e sua senha.", "erro");
        return;
    }

    botaoLogin.disabled = true;
    botaoLogin.textContent = "Entrando...";

    try {
        const resposta = await fetch("/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, senha })
        });

        const dados = await resposta.json().catch(() => ({}));

        if (!resposta.ok) {
            throw new Error(
                dados.mensagem || dados.erro || "Não foi possível entrar."
            );
        }

        const usuario = dados.usuario;

        if (usuario.perfil === "morador") {
            mostrarMensagem(
                `Login realizado com sucesso. Olá, ${usuario.nome}! Redirecionando...`,
                "sucesso"
            );
            window.setTimeout(() => {
                window.location.assign("/meus-chamados");
            }, 900);
        } else {
            mostrarMensagem(
                `Login realizado com sucesso. Olá, ${usuario.nome}!`,
                "sucesso"
            );
        }

        formulario.reset();
    } catch (erro) {
        mostrarMensagem(
            erro.message || "Erro de conexão com o servidor.",
            "erro"
        );
    } finally {
        botaoLogin.disabled = false;
        botaoLogin.textContent = "Entrar";
    }
});

function mostrarMensagem(texto, tipo) {
    mensagem.textContent = texto;
    mensagem.className = tipo === "sucesso"
        ? "mensagem-sucesso"
        : "mensagem-erro";
}

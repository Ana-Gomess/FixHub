const formulario = document.getElementById("formChamado");
const campoTitulo = document.getElementById("titulo");
const campoDescricao = document.getElementById("descricao");
const campoLocalizacao = document.getElementById("localizacao");
const mensagem = document.getElementById("mensagem");
const botaoChamado = document.getElementById("botaoChamado");

formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    limparMensagem();

    const titulo = campoTitulo.value.trim();
    const descricao = campoDescricao.value.trim();
    const localizacao = campoLocalizacao.value.trim();

    if (!titulo || !descricao || !localizacao) {
        mostrarMensagem("Preencha o título, a descrição e a localização.", "erro");
        return;
    }

    botaoChamado.disabled = true;
    botaoChamado.textContent = "Enviando...";

    try {
        const resposta = await fetch("/chamados", {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ titulo, descricao, localizacao })
        });

        const dados = await resposta.json().catch(() => ({}));

        if (!resposta.ok) {
            throw new Error(
                dados.erro || "Não foi possível registrar o chamado."
            );
        }

        const id = dados.chamado?.id;
        mostrarMensagem(
            id
                ? `Chamado #${id} registrado com sucesso.`
                : (dados.mensagem || "Chamado registrado com sucesso."),
            "sucesso"
        );
        formulario.reset();
    } catch (erro) {
        mostrarMensagem(
            erro.message || "Erro de conexão com o servidor.",
            "erro"
        );
    } finally {
        botaoChamado.disabled = false;
        botaoChamado.textContent = "Enviar chamado";
    }
});

function limparMensagem() {
    mensagem.textContent = "";
    mensagem.className = "";
}

function mostrarMensagem(texto, tipo) {
    mensagem.textContent = texto;
    mensagem.className = tipo === "sucesso"
        ? "mensagem-sucesso"
        : "mensagem-erro";
}

const formulario = document.getElementById("formChamado");
const campoTitulo = document.getElementById("titulo");
const campoDescricao = document.getElementById("descricao");
const campoLocalizacao = document.getElementById("localizacao");
const botaoChamado = document.getElementById("botaoChamado");

formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();

    const titulo = campoTitulo.value.trim();
    const descricao = campoDescricao.value.trim();
    const localizacao = campoLocalizacao.value.trim();

    if (!titulo || !descricao || !localizacao) {
        [campoTitulo, campoDescricao, campoLocalizacao]
            .find((campo) => !campo.value.trim())
            ?.focus();
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

        if (resposta.status === 401) {
            window.location.assign("/login");
            return;
        }

        if (!resposta.ok) {
            console.error(dados.erro || "Não foi possível registrar o chamado.");
            return;
        }

        window.location.assign("/meus-chamados");
    } catch (erro) {
        console.error("Erro ao enviar o chamado:", erro);
    } finally {
        botaoChamado.disabled = false;
        botaoChamado.textContent = "Enviar chamado";
    }
});

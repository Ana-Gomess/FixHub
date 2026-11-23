const formulario = document.getElementById("formChamado");
const campoTitulo = document.getElementById("titulo");
const campoDescricao = document.getElementById("descricao");
const campoLocalizacao = document.getElementById("localizacao");
const botaoChamado = document.getElementById("botaoChamado");
const mensagemChamado = document.getElementById("mensagemChamado");
const camposObrigatorios = [campoTitulo, campoDescricao, campoLocalizacao];

function limparMensagem() {
    mensagemChamado.textContent = "";
    mensagemChamado.hidden = true;
    mensagemChamado.className = "mensagem";
    mensagemChamado.setAttribute("role", "status");
    mensagemChamado.setAttribute("aria-live", "polite");
}

function mostrarMensagem(texto, tipo) {
    mensagemChamado.textContent = texto;
    mensagemChamado.hidden = false;
    mensagemChamado.className = `mensagem mensagem--${tipo}`;
    mensagemChamado.setAttribute("role", tipo === "erro" ? "alert" : "status");
    mensagemChamado.setAttribute(
        "aria-live",
        tipo === "erro" ? "assertive" : "polite"
    );
}

function mensagemDaApi(dados, alternativa) {
    return typeof dados.erro === "string" && dados.erro.trim()
        ? dados.erro
        : alternativa;
}

formulario.addEventListener("input", (evento) => {
    if (!camposObrigatorios.includes(evento.target)) {
        return;
    }

    evento.target.removeAttribute("aria-invalid");
    limparMensagem();
});

formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();
    if (botaoChamado.disabled) {
        return;
    }
    limparMensagem();

    const titulo = campoTitulo.value.trim();
    const descricao = campoDescricao.value.trim();
    const localizacao = campoLocalizacao.value.trim();

    const camposVazios = camposObrigatorios.filter(
        (campo) => !campo.value.trim()
    );
    if (camposVazios.length > 0) {
        camposVazios.forEach((campo) => campo.setAttribute("aria-invalid", "true"));
        mostrarMensagem(
            "Preencha os campos obrigatórios: título, descrição e localização.",
            "erro"
        );
        camposVazios[0].focus();
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
            mostrarMensagem(
                "Sua sessão expirou. Entre novamente antes de abrir um chamado.",
                "erro"
            );
            return;
        }

        if (resposta.status === 403) {
            mostrarMensagem(
                mensagemDaApi(
                    dados,
                    "Seu perfil não tem permissão para abrir chamados."
                ),
                "erro"
            );
            return;
        }

        if (resposta.status === 400) {
            mostrarMensagem(
                `Confira os dados informados. ${mensagemDaApi(
                    dados,
                    "Revise os campos e tente novamente."
                )}`,
                "erro"
            );
            return;
        }

        if (!resposta.ok) {
            mostrarMensagem(
                mensagemDaApi(
                    dados,
                    "Não foi possível registrar o chamado. Tente novamente."
                ),
                "erro"
            );
            return;
        }

        formulario.reset();
        camposObrigatorios.forEach((campo) => campo.removeAttribute("aria-invalid"));
        mostrarMensagem(
            typeof dados.mensagem === "string" && dados.mensagem.trim()
                ? dados.mensagem
                : "Chamado criado com sucesso.",
            "sucesso"
        );
    } catch (erro) {
        mostrarMensagem(
            "Não foi possível se comunicar com o servidor. Verifique sua conexão e tente novamente.",
            "erro"
        );
    } finally {
        botaoChamado.disabled = false;
        botaoChamado.textContent = "Enviar chamado";
    }
});

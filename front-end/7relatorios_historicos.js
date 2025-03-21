document.addEventListener("DOMContentLoaded", function () {
    const btnRelatorios = document.getElementById("btn-relatorios");
    const btnHistorico = document.getElementById("btn-historico");
    
    // Garante que "Relatórios" está ativo ao carregar a página
    btnRelatorios.classList.add("active");
    document.getElementById("relatorios-section").classList.remove("hidden");
    document.getElementById("historico-section").classList.add("hidden");

    function ativarBotao(botaoAtivo) {
        document.querySelectorAll(".action-button").forEach(botao => {
            botao.classList.remove("active");
        });
        botaoAtivo.classList.add("active");
    }

    btnRelatorios.addEventListener("click", function () {
        ativarBotao(this);
        document.getElementById("relatorios-section").classList.remove("hidden");
        document.getElementById("historico-section").classList.add("hidden");
    });

    btnHistorico.addEventListener("click", function () {
        ativarBotao(this);
        document.getElementById("historico-section").classList.remove("hidden");
        document.getElementById("relatorios-section").classList.add("hidden");
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const buttons = document.querySelectorAll(".menu-item");

    // Obtém a página atual pelo nome do arquivo
    const currentPage = window.location.pathname.split("/").pop();

    // Remove 'active-section' de todos os botões antes de ativar o correto
    buttons.forEach(button => {
        button.classList.remove("active-section"); // Remove a classe de todos

        const buttonPage = button.getAttribute("onclick").match(/'([^']+)'/)[1]; // Obtém a URL do botão

        if (buttonPage === currentPage) {
            button.classList.add("active-section"); // Ativa apenas o botão da página atual
        }
    });
});

// Função para mudar de página corretamente
function setActive(page) {
    window.location.href = page;
}

// Abre o modal para adicionar produto
function abrirModal() {
    document.getElementById("modal").style.display = "flex";
}

// Fecha o modal
function fecharModal() {
    document.getElementById("modal").style.display = "none";
}

// Fecha o modal se o usuário clicar fora dele
window.onclick = function(event) {
    let modal = document.getElementById("modal");
    if (event.target == modal) {
        fecharModal();
    }
};

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


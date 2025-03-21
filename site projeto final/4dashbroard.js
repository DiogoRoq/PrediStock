// Função para alternar o menu do usuário
function toggleMenu() {
    var menu = document.getElementById("dropdownMenu");
    menu.style.display = (menu.style.display === "block") ? "none" : "block";
}

// Fechar o menu ao clicar fora
document.addEventListener("click", function(event) {
    var userMenu = document.querySelector(".user-menu");
    if (!userMenu.contains(event.target)) {
        document.getElementById("dropdownMenu").style.display = "none";
    }
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


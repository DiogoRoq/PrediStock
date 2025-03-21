document.addEventListener("DOMContentLoaded", function() {
    // Seleciona todos os ícones de alternância de senha
    const togglePasswordIcons = document.querySelectorAll(".password-toggle i");

    togglePasswordIcons.forEach(icon => {
        const passwordInput = icon.closest(".password-container").querySelector("input");
        const toggleContainer = icon.parentElement;

        // Esconder o ícone no início
        toggleContainer.style.display = "none";

        // Alternância da visibilidade da senha
        icon.addEventListener("click", function() {
            if (passwordInput.type === "password") {
                passwordInput.type = "text"; // Exibe a senha
                icon.classList.replace("fa-eye-slash", "fa-eye"); // Alterna para olho aberto
            } else {
                passwordInput.type = "password"; // Oculta a senha
                icon.classList.replace("fa-eye", "fa-eye-slash"); // Alterna para olho fechado
            }
        });

        // Mostrar o ícone apenas quando o usuário digitar
        passwordInput.addEventListener("input", function() {
            if (passwordInput.value === "") {
                toggleContainer.style.display = "none"; // Esconder ícone se o campo estiver vazio
            } else {
                toggleContainer.style.display = "block"; // Mostrar ícone se houver texto
            }
        });
    });
});

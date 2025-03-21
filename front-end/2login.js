document.addEventListener("DOMContentLoaded", function() {
    const togglePassword = document.querySelector(".password-toggle i");            // Seleciona o ícone de alternância
    const passwordInput = document.querySelector("#password");                      // Seleciona o campo de senha
    const toggleContainer = document.querySelector(".password-toggle");             // Seleciona o contêiner do ícone

    if (togglePassword && passwordInput) {
        toggleContainer.addEventListener("click", function() {
            if (passwordInput.type === "password") {
                passwordInput.type = "text";                                      // Exibe a senha
                togglePassword.classList.replace("fa-eye-slash", "fa-eye");       // Alterna o ícone para olho aberto
            } else {
                passwordInput.type = "password";                                  // Oculta a senha
                togglePassword.classList.replace("fa-eye", "fa-eye-slash");      // Alterna o ícone para olho fechado
            }
        });

                                                                                 // Esconder o ícone até que o usuário digite algo
        passwordInput.addEventListener("input", function() {
            if (passwordInput.value === "") {
                toggleContainer.style.display = "none";                          // Esconder o ícone
            } else {
                toggleContainer.style.display = "block";                          // Mostrar o ícone
            }
        });

        
        toggleContainer.style.display = "none";                                   // Esconder o ícone no início
    }
});

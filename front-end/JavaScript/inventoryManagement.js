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

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("formAdicionar");

    if (form) {
        form.addEventListener("submit", function (e) {
            e.preventDefault(); // Prevent default form submission

            const nome = document.getElementById("nome").value;
            const descricao = document.getElementById("descricao").value;
            const preco = parseFloat(document.getElementById("preco").value);
            const quantidade = parseInt(document.getElementById("quantidade").value);
            const categoria_id = parseInt(document.getElementById("categoria").value);

            fetch("http://localhost:5000/api/add-product", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    nome,
                    descricao,
                    preco,
                    quantidade,
                    categoria_id
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.message) {
                    alert(data.message);
                    fecharModal();
                    addProductToTable({ nome, descricao, preco, quantidade, categoria_id });
                } else {
                    alert(data.error || "Erro ao adicionar produto.");
                }
            })
            .catch(error => {
                console.error("Erro:", error);
                alert("Erro ao conectar ao servidor.");
            });
        });
    }

    // Fetch and display products on page load
    fetch("http://localhost:5000/api/get-products")
        .then(response => response.json())
        .then(products => {
            const tableBody = document.getElementById("tabela-produtos");
            tableBody.innerHTML = ""; // Clear existing rows
            products.forEach(product => {
                addProductToTable(product);
            });
        })
        .catch(error => {
            console.error("Erro ao buscar produtos:", error);
        });
});

function addProductToTable({ nome, descricao, preco, quantidade, categoria_id }) {
    const tableBody = document.getElementById("tabela-produtos");

    const row = document.createElement("tr");

    const categoriaTexto = {
        1: "Produto Final",
        2: "Produto Intermédio",
        3: "Matéria-Prima"
    }[categoria_id] || "Categoria Desconhecida";

    row.innerHTML = `
        <td>${nome}</td>
        <td>${descricao}</td>
        <td>${preco.toFixed(2)}</td>
        <td>${quantidade}</td>
        <td>${categoriaTexto}</td>
    `;

    tableBody.appendChild(row);
}
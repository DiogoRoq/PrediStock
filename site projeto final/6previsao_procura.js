// Função para criar o gráfico
function createChart() {
    const ctx = document.getElementById('salesChart').getContext('2d');
    
    window.salesChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ["-5", "-4", "-3", "-2", "-1", "0"],
            datasets: [
                {
                    label: "Vendas Reais",
                    data: [50, 80, 150, 200, 180, 220],
                    borderColor: "blue",
                    backgroundColor: "rgba(0,0,255,0.2)",
                    fill: true
                },
                {
                    label: "Vendas Previstas",
                    data: [60, 90, 160, 210, 190, 150],
                    borderColor: "orange",
                    backgroundColor: "rgba(255,165,0,0.2)",
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

// Atualizar gráfico quando selecionar um produto
function updateChart() {
    const product = document.getElementById("product-select").value;

    // Simulação de novas previsões com base no produto selecionado
    let newData;
    if (product === "Produto A") {
        newData = [50, 80, 150, 200, 180, 220];
    } else if (product === "Produto B") {
        newData = [40, 60, 110, 170, 160, 210];
    } else {
        newData = [30, 50, 90, 140, 130, 190];
    }

    // Atualiza os dados do gráfico
    window.salesChart.data.datasets[0].data = newData;
    window.salesChart.update();
}

// Chamar a função para criar o gráfico quando a página carregar
window.onload = createChart;


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


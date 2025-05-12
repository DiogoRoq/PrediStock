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
            maintainAspectRatio: true, // Still flexible, but canvas height is now controlled
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
    if (window.salesChart) {
        window.salesChart.data.datasets[0].data = newData;
        window.salesChart.update();
    }
}

// Chamar a função para criar o gráfico quando a página carregar
window.addEventListener("DOMContentLoaded", function () {
    const canvas = document.getElementById('salesChart');
    
    // Evita crescimento descontrolado do canvas
    canvas.height = 300; // ou qualquer valor fixo que funcione bem no layout
    
    createChart();

    // Lógica de menu ativa
    const buttons = document.querySelectorAll(".menu-item");
    const currentPage = window.location.pathname.split("/").pop();
    buttons.forEach(button => {
        button.classList.remove("active-section");
        const buttonPage = button.getAttribute("onclick").match(/'([^']+)'/)[1];
        if (buttonPage === currentPage) {
            button.classList.add("active-section");
        }
    });
});

// Função para mudar de página corretamente
function setActive(page) {
    window.location.href = page;
}

document.getElementById('upload-form').addEventListener('submit', function (event) {
    event.preventDefault();
  
    const fileInput = document.getElementById('csv-file');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
  
    fetch('/forecast', {
      method: 'POST',
      body: formData
    })
      .then(response => response.json())
      .then(data => {
        const container = document.getElementById('forecast-results');
        if (data.error) {
          container.innerHTML = `<p style="color:red;">Error: ${data.error}</p>`;
          return;
        }
  
        let html = '<h3>Predicted Demand</h3><table border="1" cellpadding="5"><tr>';
        const keys = Object.keys(data[0]);
  
        // Table headers
        keys.forEach(key => {
          html += `<th>${key}</th>`;
        });
        html += '</tr>';
  
        // Table rows
        data.forEach(row => {
          html += '<tr>';
          keys.forEach(key => {
            html += `<td>${row[key]}</td>`;
          });
          html += '</tr>';
        });
  
        html += '</table>';
        container.innerHTML = html;
      })
      .catch(error => {
        document.getElementById('forecast-results').innerHTML = `<p style="color:red;">Request failed: ${error}</p>`;
      });
  });
  

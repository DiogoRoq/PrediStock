document.querySelector('form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const token = localStorage.getItem('token');
    const nome = document.getElementById('nome').value;
    const descricao = document.getElementById('descricao').value;
    const preco = parseFloat(document.getElementById('preco').value);
    const quantidade = parseInt(document.getElementById('quantidade').value);
    const categoria_id = parseInt(document.getElementById('categoria_id').value);

    const response = await fetch('/api/add-product', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ nome, descricao, preco, quantidade, categoria_id })
    });

    if (response.ok) {
        alert('Produto adicionado com sucesso!');
    } else {
        const error = await response.json();
        alert(`Erro: ${error.message}`);
    }
});


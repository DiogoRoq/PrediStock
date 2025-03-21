<?php
$servername = "localhost";
$username = "root";
$password = "root";
$dbname = "inventário";

// Criar conexão
$conn = new mysqli($servername, $username, $password, $dbname);

// Verificar conexão
if ($conn->connect_error) {
    die("Falha na conexão: " . $conn->connect_error);
}

// Verificar se os dados vieram do formulário
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Proteger os dados contra SQL Injection
    $nome = mysqli_real_escape_string($conn, $_POST['nome']);
    $descricao = mysqli_real_escape_string($conn, $_POST['descricao']);
    $preco = isset($_POST['preco']) ? floatval($_POST['preco']) : 0;
    $quantidade = isset($_POST['quantidade']) ? intval($_POST['quantidade']) : 0;
    $categoria_id = isset($_POST['categoria_id']) ? intval($_POST['categoria_id']) : 0;

    // Verificar se todos os campos obrigatórios estão preenchidos corretamente
    if (!empty($nome) && $preco > 0 && $quantidade > 0 && $categoria_id > 0) {
        // Comando SQL corrigido para inserção
        $sql = "INSERT INTO produtos (nome, descrição, preço, quantidade, categoria_id) 
                VALUES ('$nome', '$descricao', '$preco', '$quantidade', '$categoria_id')";

        if ($conn->query($sql) === TRUE) {
            echo "<script>alert('Produto adicionado com sucesso!'); window.location.href='gestao-produtos.html';</script>";
        } else {
            echo "<script>alert('Erro ao adicionar produto: " . $conn->error . "'); window.history.back();</script>";
        }
    } else {
        echo "<script>alert('Por favor, preencha todos os campos corretamente!'); window.history.back();</script>";
    }
}

// Fechar conexão
$conn->close();
?>

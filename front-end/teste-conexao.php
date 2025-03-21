<?php
$servername = "127.0.0.1";
$username = "root"; 
$password = "root"; 
$dbname = "inventario"; 
$port = 3306;

$conn = new mysqli($servername, $username, $password, $dbname, $port);

if ($conn->connect_error) {
    die("Falha na conexão: " . $conn->connect_error);
} else {
    echo "Conexão bem-sucedida!";
}

$conn->close();
?>
<?php
// config.php
$host = 'localhost';
$user = 'root';
$password = '';
$database = 'tambak_monitoring';

$conn = new mysqli($host, $user, $password, $database);

if ($conn->connect_error) {
    die("Koneksi database gagal: " . $conn->connect_error);
}

// Set timezone ke WIB (Asia/Jakarta)
date_default_timezone_set('Asia/Jakarta');
?>
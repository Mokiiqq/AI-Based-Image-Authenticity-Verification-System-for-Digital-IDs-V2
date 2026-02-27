<?php
include 'db.php';

$data = json_decode(file_get_contents("php://input"), true);
$username = $data['username'];

$result = $conn->query("SELECT created_at, result FROM uploads WHERE username='$username'");

$rows = [];

while($row = $result->fetch_assoc()){
    $rows[] = $row;
}

echo json_encode($rows);
?>
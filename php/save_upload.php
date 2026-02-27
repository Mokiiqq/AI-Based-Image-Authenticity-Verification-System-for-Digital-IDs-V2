<?php
include 'db.php';

header("Content-Type: application/json");

$data = json_decode(file_get_contents("php://input"), true);

$username = $data['username'];
$image = $data['image'];
$result = $data['result'];

$stmt = $conn->prepare("INSERT INTO uploads (username, image, result) VALUES (?, ?, ?)");
$stmt->bind_param("sss", $username, $image, $result);
$stmt->execute();

echo json_encode(["success"=>true]);
?>
<?php
include 'db.php';

header("Content-Type: application/json");

// receive JSON
$data = json_decode(file_get_contents("php://input"), true);

$username = $data['username'];
$password = $data['password'];

// check user
$stmt = $conn->prepare("SELECT password FROM users WHERE username=?");
$stmt->bind_param("s", $username);
$stmt->execute();
$result = $stmt->get_result();

if ($result->num_rows === 0) {
    echo json_encode([
        "success" => false,
        "message" => "User not found"
    ]);
    exit();
}

$row = $result->fetch_assoc();

// verify password
if (password_verify($password, $row['password'])) {
    echo json_encode([
        "success" => true
    ]);
} else {
    echo json_encode([
        "success" => false,
        "message" => "Invalid password"
    ]);
}
?>
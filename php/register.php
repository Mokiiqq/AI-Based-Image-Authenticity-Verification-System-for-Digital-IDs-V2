<?php
include 'db.php';

$username = $_POST['username'];
$password = $_POST['password'];
$confirm = $_POST['confirm_password'];

if ($password !== $confirm) {
    echo "Password does not match";
    exit();
}

// hash password for security
$hashedPassword = password_hash($password, PASSWORD_DEFAULT);

// check if username exists
$check = $conn->prepare("SELECT * FROM users WHERE username=?");
$check->bind_param("s", $username);
$check->execute();
$result = $check->get_result();

if ($result->num_rows > 0) {
    echo "Username already exists";
    exit();
}

// insert user
$stmt = $conn->prepare("INSERT INTO users (username, password) VALUES (?, ?)");
$stmt->bind_param("ss", $username, $hashedPassword);

if ($stmt->execute()) {
    echo "Registration Successful";
} else {
    echo "Error";
}
?>
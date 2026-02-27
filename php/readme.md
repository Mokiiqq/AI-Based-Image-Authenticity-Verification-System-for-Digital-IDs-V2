important create database in mysql

CREATE DATABASE users_db;

USE users_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    password VARCHAR(255)
);

CREATE TABLE uploads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    image LONGTEXT,
    result VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
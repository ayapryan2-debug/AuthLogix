CREATE DATABASE authlogix_db;
USE authlogix_db;
CREATE TABLE access_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255),
    ip_address VARCHAR(45),
    status ENUM('pending', 'approved', 'denied') DEFAULT 'pending',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
# AUTHLOGIX // MESH-CORE SOC COMMAND
> A Lightweight Forensic & Intrusion Monitoring Dashboard built with Flask.

PHALANX is a security-focused web interface designed to intercept, log, and manage network access requests in real-time. It features a SOC (Security Operations Center) dashboard with live metrics, terminal-style logs, and manual firewall controls.

# Directories of the Files
    AuthLogix/
    │
    ├── static/
    │   ├── history_style.css
    │   ├── login.css
    │   ├── protected-vault.css
    │   └── soc_style.css
    │
    ├── templates/
    │   ├── history.html
    │   ├── index.html
    │   ├── login.html
    │   └── protected-vault.html
    │
    ├── app.py
    ├── authlogix.service
    ├── database.sql
    ├── README.md
    └── requirements.txt

# Installation & Setup on a VM

1. Update and Prepare System
# Open your VM terminal and ensure your package list is updated:
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv -y

2. Clone or Upload Files
Navigate to your project directory (e.g., /home/user/authlogix). If you're uploading via SFTP or manual copy, ensure all files from the structure above are present.

3. Create a Virtual Environment (Recommended)
# This keeps your system clean and prevents tool conflicts:
python3 -m venv venv
source venv/bin/activate

4. Database Setup with MYSQL
sudo mysql
CREATE DATABASE authlogix_db;
USE authlogix_db;
CREATE TABLE access_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255),
    ip_address VARCHAR(45),
    status ENUM('pending', 'approved', 'denied') DEFAULT 'pending',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

5. Create systemd service file
sudo nano /etc/systemd/system/authlogix.service

# Paste this to authlogix.service
[Unit]
Description=Gunicorn instance to serve AuthLogix
After=network.target

[Service]
User=your-username
Group=www-data
WorkingDirectory=/home/your-username/authlogix
ExecStart=/usr/bin/gunicorn app:app
Restart=always

[Install]
WantedBy=multi-user.target

# Enable Service
sudo systemctl daemon-reload
sudo systemctl enable authlogix
sudo systemctl start authlogix

# Check the status 
sudo systemctl status authlogix

5. Install Dependecies
# Use the requirements.txt file to install all necessary tools
pip install -r requirements.txt

6. Setup Firewall
# Since the dashboard displays UFW status, ensure it is active on your VM:
sudo ufw enable
sudo ufw allow 5001/tcp  # Allow the Web UI Port
sudo ufw allow 22/tcp    # Keep SSH open to avoid lockout!

7. Running the Application
# To start the AuthLogix SOC Command:
python3 app.py

# Access the dashboard via browser:
 - Local: http://localhost:5001
 - Remote (VM IP): http://<YOUR_VM_IP>:5001


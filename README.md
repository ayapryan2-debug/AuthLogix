## 📂 Project Structure

```text
AuthLogix/
│
├── static/
│   ├── history_style.css      # Audit logs styling
│   ├── login.css              # Auth page styling
│   ├── protected-vault.css    # Intercepted route styling
│   └── soc_style.css          # Main SOC dashboard UI
│
├── templates/
│   ├── history.html           # Forensic logs view
│   ├── index.html             # SOC Command Center
│   ├── login.html             # Admin portal
│   └── protected-vault.html   # Simulated target resource
│
├── app.py                     # Backend Logic & Interceptor
├── authlogix.service          # Systemd configuration
├── database.sql               # Database schema
├── README.md                  # Documentation
└── requirements.txt              # Dependencies
|__ .gitignore

Installation & Setup (Linux/VM)
1. System Update
Bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv ufw mysql-server -y

2. Clone / Upload Project
Place the project folder in your VM (e.g., /home/user/authlogix).

3. Create Virtual Environment
Bash
python3 -m venv venv
source venv/bin/activate

4. Install Dependencies
Bash
pip install -r requirements.txt

5. MySQL Database Setup
Log in to MySQL (sudo mysql) and run:

SQL
CREATE DATABASE authlogix_db;
USE authlogix_db;

CREATE TABLE access_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255),
    ip_address VARCHAR(45),
    status ENUM('pending', 'approved', 'denied') DEFAULT 'pending',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

6. Firewall Setup (UFW)
Bash
sudo ufw enable
sudo ufw allow 5001/tcp
sudo ufw allow 22/tcp


Running the Application
Option A: Development Mode
Bash
python3 app.py
Local: http://localhost:5001

Remote: http://<VM_IP>:5001

Option B: Production Deployment (systemd)
Create service file: sudo nano /etc/systemd/system/authlogix.service

Paste configuration:

Ini, TOML
[Unit]
Description=AuthLogix Gunicorn Service
After=network.target

[Service]
User=your-username
Group=www-data
WorkingDirectory=/home/your-username/authlogix
ExecStart=/home/your-username/authlogix/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5001 app:app
Restart=always

[Install]
WantedBy=multi-user.target
Enable and Start:

Bash
sudo systemctl daemon-reload
sudo systemctl enable authlogix
sudo systemctl start authlogix

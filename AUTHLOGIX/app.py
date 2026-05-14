from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import mysql.connector
import subprocess
import socket

app = Flask(__name__)
app.secret_key = "phalanx_2026_secure_key"

# --- DATABASE CONFIG ---
db_config = {
    'host': 'localhost',
    'user': 'auth_admin',
    'password': 'Admin123!',
    'database': 'authlogix_db'
}

def query_db(query, args=(), one=False, commit=False):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    
    # Siguraduhin na +8 (Manila Time) ang session para sa database logs
    cursor.execute("SET time_zone = '+08:00'")
    
    cursor.execute(query, args)
    if commit:
        conn.commit()
        result = cursor.lastrowid
    else:
        result = cursor.fetchall()
    conn.close()
    return (result[0] if result else None) if one else result

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# --- API FOR REAL-TIME QUEUE ---
@app.route('/api/pending_requests')
def api_pending_requests():
    if 'user' not in session: return jsonify([])
    
    # Formatted Date: MM/DD/YY HH:MM using CONCAT to avoid % errors
    query = """
        SELECT id, username, ip_address, status, 
        CONCAT(MONTH(timestamp), '/', DAY(timestamp), '/', YEAR(timestamp), ' ', HOUR(timestamp), ':', MINUTE(timestamp)) as short_stamp 
        FROM access_requests 
        WHERE status='pending' 
        ORDER BY id DESC
    """
    requests = query_db(query)
    return jsonify(requests)

# --- MAIN DASHBOARD ---
@app.route('/')
def home():
    if 'user' not in session: return redirect(url_for('login'))
    
    try:
        ram_usage = subprocess.check_output("free | grep Mem | awk '{print $3/$2 * 100.0}'", shell=True).decode("utf-8").strip()[:4] + "%"
        cpu_usage = subprocess.check_output("top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\\([0-9.]*\\)%* id.*/\\1/' | awk '{print 100 - $1}'", shell=True).decode("utf-8").strip()[:4] + "%"
        ufw_raw = subprocess.check_output(["sudo", "ufw", "status", "numbered"]).decode("utf-8")
    except:
        ram_usage, cpu_usage, ufw_raw = "N/A", "N/A", "ERROR: UFW Service Unreachable."

    return render_template("index.html", ufw_status=ufw_raw, cpu=cpu_usage, ram=ram_usage)

# --- GATEKEEPER ROUTE (Interception) ---
@app.route('/protected-vault')
def protected_vault():
    user_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')

    # --- HYBRID IDENTITY LOGIC ---
    device_identity = "Unknown Node"
    if "Android" in user_agent:
        device_identity = "Android Mobile"
    elif "iPhone" in user_agent:
        device_identity = "Apple iPhone"
    elif "Windows" in user_agent or "Macintosh" in user_agent or "Linux" in user_agent:
        try:
            host_info = socket.gethostbyaddr(user_ip)
            device_identity = host_info[0].split('.')[0].upper()
        except:
            os_label = "Windows PC" if "Windows" in user_agent else "Workstation"
            device_identity = f"{os_label} ({user_ip.split('.')[-1]})"

    check = query_db("SELECT status FROM access_requests WHERE ip_address=%s ORDER BY id DESC LIMIT 1", (user_ip,), one=True)
    
    style = """
    <style>
        body { background: #05070a; color: #e6edf3; font-family: 'Courier New', monospace; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; overflow: hidden; }
        .lock-container { text-align: center; border: 1px solid #ff3e3e; padding: 40px; background: rgba(255, 62, 62, 0.05); border-radius: 8px; box-shadow: 0 0 20px rgba(255, 62, 62, 0.2); max-width: 500px; position: relative; }
        .pending-mode { border-color: #f2cc60; background: rgba(242, 204, 96, 0.05); box-shadow: 0 0 20px rgba(242, 204, 96, 0.2); }
        .glitch { font-size: 2rem; font-weight: bold; text-transform: uppercase; letter-spacing: 5px; margin-bottom: 20px; }
        .status-box { background: #000; padding: 15px; border-radius: 4px; border: 1px solid #333; margin: 20px 0; font-size: 0.9rem; text-align: left; line-height: 1.6; }
        .scanline { width: 100%; height: 2px; background: rgba(255, 255, 255, 0.1); position: absolute; top: 0; left: 0; animation: scan 3s linear infinite; }
        @keyframes scan { 0% { top: 0; } 100% { top: 100%; } }
        .pulse { animation: pulse-anim 2s infinite; }
    </style>
    """

    if not check:
        query_db("INSERT INTO access_requests (username, ip_address, status) VALUES (%s, %s, %s)", 
                 (device_identity, user_ip, 'pending'), commit=True)
        return f"<html>{style}<body><div class='lock-container'><div class='scanline'></div><div class='glitch' style='color: #ff3e3e;'>ACCESS_DENIED</div><div class='status-box'><span style='color: #ff3e3e;'>[!] ALERT:</span> Unauthorized access attempt.<br><span style='color: #8b949e;'>ORIGIN:</span> {user_ip}<br><span style='color: #8b949e;'>IDENTITY:</span> {device_identity}</div><p class='pulse' style='color: #8b949e;'>Network signature logged.</p></div></body></html>"

    if check['status'] == 'approved':
        return render_template("vault.html")
    
    status_color = "#f2cc60" if check['status'] == 'pending' else "#ff3e3e"
    status_msg = "AWAITING_VALIDATION" if check['status'] == 'pending' else "PERMANENT_RESTRICTION"
    
    return f"<html>{style}<body><div class='lock-container pending-mode' style='border-color: {status_color};'><div class='scanline'></div><div class='glitch' style='color: {status_color};'>{status_msg}</div><div class='status-box'><span style='color: {status_color};'>[*] STATUS:</span> Request queued.<br><span style='color: #8b949e;'>DEVICE:</span> {device_identity}<br><span style='color: #8b949e;'>ACTION:</span> Wait for Admin review.</div></div></body></html>"

# --- ACTIONS (ALLOW/BLOCK) ---
@app.route('/allow/<int:req_id>')
def allow(req_id):
    if 'user' not in session: return redirect(url_for('login'))
    target = query_db("SELECT * FROM access_requests WHERE id=%s", (req_id,), one=True)
    if target:
        ip = target['ip_address']
        # 1. UFW Action
        subprocess.run(["sudo", "ufw", "delete", "deny", "from", ip, "to", "any", "port", "5001"])
        subprocess.run(["sudo", "ufw", "insert", "1", "allow", "from", ip, "to", "any", "port", "5001"])
        
        # 2. LOG TO HISTORY
        query_db("INSERT INTO access_requests (username, ip_address, status) VALUES (%s, %s, 'approved')", 
                 (target['username'], ip), commit=True)
        
        # 3. DELETE PENDING
        query_db("DELETE FROM access_requests WHERE id=%s", (req_id,), commit=True)
        
    return redirect(url_for('home'))

@app.route('/block/<int:req_id>')
def block(req_id):
    if 'user' not in session: return redirect(url_for('login'))
    target = query_db("SELECT * FROM access_requests WHERE id=%s", (req_id,), one=True)
    if target:
        ip = target['ip_address']
        # 1. UFW Action
        subprocess.run(["sudo", "ufw", "delete", "allow", "from", ip, "to", "any", "port", "5001"])
        subprocess.run(["sudo", "ufw", "insert", "1", "deny", "from", ip, "to", "any", "port", "5001"])
        
        # 2. LOG TO HISTORY
        query_db("INSERT INTO access_requests (username, ip_address, status) VALUES (%s, %s, 'denied')", 
                 (target['username'], ip), commit=True)
        
        # 3. DELETE PENDING
        query_db("DELETE FROM access_requests WHERE id=%s", (req_id,), commit=True)
        
    return redirect(url_for('home'))

# --- MANUAL MANAGEMENT (MULTI-PURPOSE) ---
@app.route('/manual_cmd', methods=['POST'])
def manual_cmd():
    if 'user' not in session: return redirect(url_for('login'))
    ip = request.form.get('manual_ip')
    port = request.form.get('manual_port')
    action = request.form.get('manual_action')
    
    if ip and port and action:
        # STEP 1: Refresh Rule (Delete before Insert)
        subprocess.run(["sudo", "ufw", "delete", "allow", "from", ip, "to", "any", "port", port])
        subprocess.run(["sudo", "ufw", "delete", "deny", "from", ip, "to", "any", "port", port])
        
        # STEP 2: Priority Insert
        subprocess.run(["sudo", "ufw", "insert", "1", action, "from", ip, "to", "any", "port", port])

        # STEP 3: DB Update
        new_status = 'approved' if action == 'allow' else 'denied'
        manual_tag = f"MANUAL-{action.upper()} (Port {port})"
        
        existing = query_db("SELECT id FROM access_requests WHERE ip_address=%s ORDER BY id DESC LIMIT 1", (ip,), one=True)
        if existing:
            query_db("UPDATE access_requests SET status=%s, username=%s WHERE id=%s", 
                     (new_status, manual_tag, existing['id']), commit=True)
        else:
            query_db("INSERT INTO access_requests (username, ip_address, status) VALUES (%s, %s, %s)", 
                     (manual_tag, ip, new_status), commit=True)
                     
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form.get('username') == "admin" and request.form.get('password') == "admin":
            session['user'] = "Administrator"
            return redirect(url_for('home'))
        error = "Invalid Credentials"
    return render_template("login.html", is_admin=True, error=error)

@app.route('/history')
def history_page():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template("history.html")

@app.route('/api/history_logs')
def api_history_logs():
    if 'user' not in session: return jsonify([])
    
    # CONCAT used here as well for consistent formatting without % escaping issues
    query = """
        SELECT id, username, ip_address, status, 
        CONCAT(MONTH(timestamp), '/', DAY(timestamp), '/', YEAR(timestamp), ' ', HOUR(timestamp), ':', MINUTE(timestamp)) as short_stamp 
        FROM access_requests 
        WHERE status != 'pending' 
        ORDER BY id DESC LIMIT 100
    """
    requests = query_db(query)
    return jsonify(requests)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
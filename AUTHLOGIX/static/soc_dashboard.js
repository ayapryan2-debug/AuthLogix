    console.log("CPU:", CPU);
    console.log("RAM:", RAM);
    
    function updateDashboard() {
        fetch('/api/pending_requests').then(res => res.json()).then(data => {
            const tbody = document.getElementById('request-queue');
            if (data.length === 0) {
                tbody.innerHTML = "<tr><td colspan='4' style='text-align:center; padding: 50px; color: #444;'>LISTENING FOR INTRUSIONS...</td></tr>";
                return;
            }
            tbody.innerHTML = "";
            data.forEach(req => {
                tbody.innerHTML += `
                    <tr>
                        <td><span class="timestamp-label">${req.short_stamp}</span></td>
                        <td>
                            <div style="font-weight: bold;">${req.username}</div>
                            <div style="font-size: 0.6rem; color: #8b949e;">ID: ${req.id}</div>
                        </td>
                        <td><span class="ip-signature">${req.ip_address}</span></td>
                        <td>
                            <div class="action-group">
                                <a href="/allow/${req.id}" class="btn-action btn-allow">ALLOW</a>
                                <a href="/block/${req.id}" class="btn-action btn-deny">DENY</a>
                            </div>
                        </td>
                    </tr>`;
            });
        });
    }
    
    setInterval(updateDashboard, 3000); 
    updateDashboard();

    const c = document.getElementById('console'); 
    c.scrollTop = c.scrollHeight;
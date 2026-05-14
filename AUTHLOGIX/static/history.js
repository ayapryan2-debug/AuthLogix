 function updateClock() {
        document.getElementById('clock').innerText = new Date().toLocaleTimeString();
    }
    setInterval(updateClock, 1000);

    function loadHistory() {
        fetch('/api/history_logs')
            .then(res => res.json())
            .then(data => {
                const tbody = document.getElementById('historyBody');
                tbody.innerHTML = '';
                let allows = 0, denies = 0;
                let uniqueNodes = new Set();

                data.forEach(log => {
                    if(log.status === 'approved') allows++; else denies++;
                    uniqueNodes.add(log.ip_address);
                    
                    const tagClass = log.status === 'approved' ? 'tag-approved' : 'tag-denied';
                    
                    tbody.innerHTML += `
                        <tr>
                            <td class="time-col">${log.short_stamp}</td>
                            <td class="id-col">${log.username}</td>
                            <td><code>${log.ip_address}</code></td>
                            <td><span class="status-tag ${tagClass}">${log.status}</span></td>
                        </tr>
                    `;
                });

                document.getElementById('count-total').innerText = data.length;
                document.getElementById('count-allow').innerText = allows;
                document.getElementById('count-deny').innerText = denies;
                document.getElementById('count-nodes').innerText = uniqueNodes.size;
            });
    }

    function filterLogs() {
        let input = document.getElementById('logSearch').value.toUpperCase();
        let tr = document.getElementById('historyTable').getElementsByTagName('tr');
        for (let i = 1; i < tr.length; i++) {
            let text = tr[i].textContent || tr[i].innerText;
            tr[i].style.display = text.toUpperCase().indexOf(input) > -1 ? "" : "none";
        }
    }

    loadHistory();
    setInterval(loadHistory, 5000);
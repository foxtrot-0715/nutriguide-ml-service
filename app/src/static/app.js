let currentUserId = localStorage.getItem('userId');

function saveUserSession(id, name) {
    localStorage.setItem('userId', id);
    localStorage.setItem('userName', name);
}

function handleLogout() {
    if (confirm("Выйти из системы?")) {
        localStorage.clear();
        location.reload();
    }
}

async function handleLogin() {
    const username = document.getElementById('loginName').value;
    const password = document.getElementById('loginPass').value;
    if (!username) return alert("Введите имя!");

    const response = await fetch('/auth/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ username, password: password || '123', email: 'login@dummy.com' })
    });
    if (response.ok) {
        const user = await response.json();
        saveUserSession(user.id, user.username);
        location.reload();
    } else alert("Пользователь не найден");
}

async function handleRegister() {
    const username = document.getElementById('regName').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPass').value;
    const response = await fetch('/auth/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ username, email, password })
    });
    if (response.ok) {
        const user = await response.json();
        saveUserSession(user.id, user.username);
        location.reload();
    } else alert("Ошибка регистрации");
}

function checkAuth(event) {
    if (event) event.preventDefault();
    if (!currentUserId) {
        alert("Пожалуйста, войдите в систему!");
        new bootstrap.Tab(document.getElementById('auth-tab')).show();
    } else {
        const btn = document.getElementById('cabinet-tab');
        btn.setAttribute('data-bs-toggle', 'tab');
        btn.setAttribute('data-bs-target', '#cabinet');
        new bootstrap.Tab(btn).show();
        updateBalance();
        updateTasks();
    }
}

async function updateBalance() {
    if (!currentUserId) return;
    try {
        const res = await fetch(`/users/${currentUserId}/balance`);
        const data = await res.json();
        document.getElementById('balanceAmount').innerText = data.credits;
    } catch (e) { console.error("Balance error:", e); }
}

async function makeDeposit() {
    const amount = document.getElementById('depositAmount').value;
    await fetch(`/users/${currentUserId}/deposit`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ amount: parseInt(amount) })
    });
    updateBalance();
}

async function sendPredict() {
    const data = document.getElementById('predictInput').value;
    if (!data) return alert("Введите данные!");
    
    const res = await fetch(`/predict/${currentUserId}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ data })
    });
    if (res.status === 402) alert("Недостаточно кредитов!");
    else {
        updateBalance();
        updateTasks();
        document.getElementById('predictInput').value = '';
    }
}

async function updateTasks() {
    if (!currentUserId) return;
    try {
        const res = await fetch(`/users/${currentUserId}/tasks`);
        const tasks = await res.json();
        const tbody = document.getElementById('tasksHistory');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        if (tasks.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">История пока пуста</td></tr>';
            return;
        }

        tasks.forEach(t => {
            const dateStr = t.created_at ? new Date(t.created_at).toLocaleString() : 'Только что';
            const statusBadge = t.status === 'completed' ? 'success' : 'warning';
            tbody.innerHTML += `<tr>
                <td><small>${dateStr}</small></td>
                <td>${t.task_id}</td>
                <td><span class="badge bg-${statusBadge}">${t.status}</span></td>
                <td>${t.result || '<i>В обработке...</i>'}</td>
            </tr>`;
        });
    } catch (err) { console.error("History update error:", err); }
}

// Инициализация при загрузке
if (currentUserId) {
    document.getElementById('userBadge').classList.remove('d-none');
    document.getElementById('currentUserId').innerText = currentUserId;
    document.getElementById('currentUsername').innerText = localStorage.getItem('userName');
    
    const btn = document.getElementById('cabinet-tab');
    btn.setAttribute('data-bs-toggle', 'tab');
    btn.setAttribute('data-bs-target', '#cabinet');
    
    updateBalance();
    updateTasks();
    setInterval(updateTasks, 5000);
}

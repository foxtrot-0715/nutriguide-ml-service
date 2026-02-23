let currentUserId = localStorage.getItem('userId');

async function updateBalance() {
    if (!currentUserId) return;
    try {
        const res = await fetch(`/users/${currentUserId}/balance`);
        const data = await res.json();
        document.getElementById('balanceAmount').innerText = data.credits;
    } catch (e) { console.error("Balance update failed"); }
}

async function updateTransactions() {
    if (!currentUserId) return;
    try {
        const res = await fetch(`/users/${currentUserId}/transactions`);
        const txs = await res.json();
        const tbody = document.getElementById('transHistory');
        if (!tbody) return;
        tbody.innerHTML = txs.map(t => `
            <tr>
                <td><small>${new Date(t.created_at).toLocaleString('ru-RU')}</small></td>
                <td>${t.amount > 0 ? '🟢 Пополнение' : '🔴 Списание'}</td>
                <td><strong>${t.amount}</strong></td>
            </tr>
        `).join('') || '<tr><td colspan="3" class="text-center">Нет транзакций</td></tr>';
    } catch (e) { console.error("Transactions update failed"); }
}

async function updateTasks() {
    if (!currentUserId) return;
    try {
        const res = await fetch(`/users/${currentUserId}/tasks`);
        const tasks = await res.json();
        const tbody = document.getElementById('tasksHistory');
        if (!tbody) return;
        
        // В твоем main.py нет эндпоинта /users/{id}/tasks, 
        // Если история не грузится, дай знать — добавим его в main.py
        tbody.innerHTML = tasks.map(t => `
            <tr>
                <td><small>${new Date(t.created_at).toLocaleString('ru-RU')}</small></td>
                <td>${t.task_id}</td>
                <td><span class="badge bg-${t.status === 'completed' ? 'success' : 'warning'}">${t.status}</span></td>
                <td>${t.result || '...'}</td>
            </tr>
        `).join('') || '<tr><td colspan="4" class="text-center">Нет запросов</td></tr>';
    } catch (e) { console.error("Tasks update failed"); }
}

async function handleLogin() {
    const nameInput = document.getElementById('loginName');
    const passInput = document.getElementById('loginPass');

    const username = nameInput.value;
    const password = passInput.value;

    if (!username || !password) {
        return alert("Введите имя и пароль!");
    }

    try {
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ 
                username: username, 
                password: password, 
                email: 'test@test.com' 
            })
        });

        if (response.ok) {
            const user = await response.json();
            // ИСПРАВЛЕНО: Сохраняем напрямую в localStorage
            localStorage.setItem('userId', user.id);
            localStorage.setItem('userName', user.username);
            location.reload();
        } else {
            alert("Ошибка входа: проверьте имя и пароль");
        }
    } catch (err) {
        console.error("Login request failed", err);
    }
}

async function handleRegister() {
    const username = document.getElementById('regName').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPass').value;
    
    if (!username || !password || !email) return alert("Заполните все поля!");

    try {
        const response = await fetch('/auth/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ username, email, password })
        });
        if (response.ok) {
            const user = await response.json();
            localStorage.setItem('userId', user.id);
            localStorage.setItem('userName', user.username);
            location.reload();
        } else { alert("Ошибка регистрации!"); }
    } catch (err) { console.error("Register failed", err); }
}

function handleLogout() {
    localStorage.clear();
    location.reload();
}

async function makeDeposit() {
    const amount = document.getElementById('depositAmount').value;
    const res = await fetch(`/users/${currentUserId}/deposit`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ amount: parseInt(amount) })
    });
    if (res.ok) {
        await updateBalance();
        await updateTransactions();
    }
}

async function sendPredict() {
    const input = document.getElementById('predictInput');
    const res = await fetch(`/predict/${currentUserId}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ data: input.value })
    });
    if (res.ok) {
        input.value = '';
        await updateBalance();
        await updateTasks();
        await updateTransactions();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    if (currentUserId) {
        const userBadge = document.getElementById('userBadge');
        if (userBadge) userBadge.classList.remove('d-none');
        
        const usernameEl = document.getElementById('currentUsername');
        const userIdEl = document.getElementById('currentUserId');
        if (usernameEl) usernameEl.innerText = localStorage.getItem('userName');
        if (userIdEl) userIdEl.innerText = currentUserId;
        
        const cabinetBtn = document.getElementById('cabinet-tab');
        if (cabinetBtn) {
            setTimeout(() => cabinetBtn.click(), 100);
        }

        updateBalance();
        updateTasks();
        updateTransactions();
        setInterval(updateTasks, 5000);
    }
});

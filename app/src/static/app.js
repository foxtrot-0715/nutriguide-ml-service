window.currentUserId = localStorage.getItem('userId');

// --- 1. Навигация и Видимость ---
window.showTab = function(tabName) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.add('d-none'));
    const section = document.getElementById(tabName + 'Section');
    if (section) section.classList.remove('d-none');
    
    if (tabName === 'login' || tabName === 'register') {
        document.getElementById('nav-login-btn')?.classList.toggle('active', tabName === 'login');
        document.getElementById('nav-reg-btn')?.classList.toggle('active', tabName === 'register');
    }
};

window.updateUI = function() {
    const isLoggedIn = !!window.currentUserId;
    const welcome = document.getElementById('welcomeSection');
    const cabinet = document.getElementById('cabinetSection');
    const userBadge = document.getElementById('userBadge');

    if (isLoggedIn) {
        if (welcome) welcome.classList.add('d-none');
        if (cabinet) cabinet.classList.remove('d-none');
        if (userBadge) userBadge.classList.remove('d-none');
        window.showTab('cabinet');
    } else {
        if (welcome) welcome.classList.remove('d-none');
        if (cabinet) cabinet.classList.add('d-none');
        if (userBadge) userBadge.classList.add('d-none');
        window.showTab('login');
    }
};

// --- 2. Авторизация ---
window.login = async function() {
    const u = document.getElementById('loginUser').value;
    const p = document.getElementById('loginPass').value;
    try {
        const res = await fetch('/auth/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: u, password: p})
        });
        if (res.ok) {
            const data = await res.json();
            localStorage.setItem('userId', data.id);
            localStorage.setItem('userName', data.username);
            window.currentUserId = data.id;
            location.reload();
        } else {
            alert("Ошибка входа: неверный логин или пароль");
        }
    } catch (e) { alert("Сервер недоступен"); }
};

window.register = async function() {
    const u = document.getElementById('regUser').value;
    const e = document.getElementById('regEmail').value;
    const p = document.getElementById('regPass').value;
    try {
        const res = await fetch('/auth/register', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: u, email: e, password: p})
        });
        if (res.ok) {
            alert("Регистрация успешна!");
            window.showTab('login');
        } else {
            alert("Ошибка регистрации");
        }
    } catch (ex) { alert("Сервер недоступен"); }
};

window.logout = function() {
    localStorage.clear();
    window.currentUserId = null;
    location.reload();
};

// --- 3. Кабинет ---
window.updateBalance = async function() {
    if (!window.currentUserId) return;
    const res = await fetch(`/users/${window.currentUserId}/balance`);
    const data = await res.json();
    document.getElementById('balanceAmount').innerText = data.credits;
};

window.updateTransactions = async function() {
    if (!window.currentUserId) return;
    const res = await fetch(`/users/${window.currentUserId}/transactions`);
    const txs = await res.json();
    const tbody = document.getElementById('transHistory');
    if (!tbody) return;
    tbody.innerHTML = txs.map(t => `
        <tr>
            <td><small>${new Date(t.created_at).toLocaleString('ru-RU')}</small></td>
            <td>${t.type === 'refund_empty_request' ? '🔄 Возврат' : (t.amount > 0 ? '🟢 Пополнение' : '🔴 Списание')}</td>
            <td><strong>${t.amount}</strong></td>
        </tr>
    `).join('') || '<tr><td colspan="3" class="text-center text-muted">История пуста</td></tr>';
};

window.updateTasks = async function() {
    if (!window.currentUserId) return;
    const res = await fetch(`/users/${window.currentUserId}/tasks`);
    const tasks = await res.json();
    const tbody = document.getElementById('tasksHistory');
    if (!tbody) return;
    tbody.innerHTML = tasks.map(t => `
        <tr>
            <td><small>${new Date(t.created_at).toLocaleString('ru-RU')}</small></td>
            <td>#${t.task_id || t.id}</td>
            <td><span class="badge ${t.status === 'completed' ? 'bg-success' : 'bg-warning'}">${t.status}</span></td>
            <td>${t.result || '<span class="text-muted small">Обработка...</span>'}</td>
        </tr>
    `).join('') || '<tr><td colspan="4" class="text-center text-muted">Запросов нет</td></tr>';
};

// Функция отправки (валидация на стороне клиента убрана для теста возврата средств)
window.sendPredict = async function() {
    const input = document.getElementById('predictInput');
    const content = input.value; // Отправляем как есть, даже если пусто

    try {
        const res = await fetch(`/predict/${window.currentUserId}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ data: content })
        });

        if (res.ok) {
            input.value = '';
            alert("Запрос отправлен!");
        } else {
            const err = await res.json();
            // Здесь ловим 400 ошибку от бэкенда при пустом запросе
            alert(err.detail || "Произошла ошибка");
        }
    } catch (e) {
        alert("Ошибка связи с сервером");
    } finally {
        // Сразу обновляем баланс и транзакции, чтобы увидеть +10 возвратных
        await window.updateBalance();
        await window.updateTransactions();
        await window.updateTasks();
    }
};

window.deposit = async function() {
    const amount = prompt("Сумма пополнения:");
    if (!amount || isNaN(amount)) return;
    await fetch(`/users/${window.currentUserId}/deposit`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ amount: parseFloat(amount) })
    });
    await window.updateBalance();
    await window.updateTransactions();
};

document.addEventListener('DOMContentLoaded', () => {
    window.updateUI();
    if (window.currentUserId) {
        document.getElementById('currentUsername').innerText = localStorage.getItem('userName') || 'User';
        document.getElementById('currentUserId').innerText = window.currentUserId;
        window.updateBalance();
        window.updateTasks();
        window.updateTransactions();
        setInterval(window.updateTasks, 5000);
    }
});

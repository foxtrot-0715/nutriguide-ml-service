let currentUserId = localStorage.getItem('userId');

// 1. Регистрация (Пункт 2 ТЗ)
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
        alert('Успешная регистрация!');
        location.reload(); // Перезагрузим, чтобы открылся кабинет
    } else {
        const err = await response.json();
        alert('Ошибка: ' + (err.detail || 'Не удалось зарегистрироваться'));
    }
}

function saveUserSession(id, name) {
    localStorage.setItem('userId', id);
    localStorage.setItem('userName', name);
}

// 2. Инициализация кабинета
if (currentUserId) {
    document.getElementById('cabinet-tab').classList.remove('disabled');
    document.getElementById('userBadge').classList.remove('d-none');
    document.getElementById('currentUserId').innerText = currentUserId;
    document.getElementById('currentUsername').innerText = localStorage.getItem('userName');
    
    // Переключим на кабинет автоматически
    const cabinetTab = new bootstrap.Tab(document.getElementById('cabinet-tab'));
    cabinetTab.show();
    
    updateBalance();
    updateTasks();
    setInterval(updateTasks, 5000);
}

// 3. Работа с балансом
async function updateBalance() {
    const response = await fetch(`/users/${currentUserId}/balance`);
    const data = await response.json();
    document.getElementById('balanceAmount').innerText = data.credits;
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

// 4. ML-запрос и История
async function sendPredict() {
    const data = document.getElementById('predictInput').value;
    const response = await fetch(`/predict/${currentUserId}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ data })
    });
    
    if (response.status === 402) alert('Пополните баланс!');
    else if (response.ok) { updateTasks(); updateBalance(); }
}

async function updateTasks() {
    const response = await fetch(`/users/${currentUserId}/tasks`);
    const tasks = await response.json();
    const tbody = document.getElementById('tasksHistory');
    tbody.innerHTML = '';

    tasks.reverse().forEach(t => {
        const date = t.created_at ? new Date(t.created_at).toLocaleString() : '---';
        tbody.innerHTML += `<tr>
            <td><small>${date}</small></td>
            <td>${t.task_id}</td>
            <td><span class="badge bg-${t.status === 'completed' ? 'success' : 'warning'}">${t.status}</span></td>
            <td>-10 🪙</td>
            <td>${t.result || '<i>В обработке...</i>'}</td>
        </tr>`;
    });
}

// Функция выхода (Logout)
function handleLogout() {
    if (confirm("Вы уверены, что хотите выйти?")) {
        localStorage.removeItem('userId');
        localStorage.removeItem('userName');
        alert("Вы вышли из системы");
        location.reload(); // Возвращает на главную страницу (вкладка "О сервисе")
    }
}

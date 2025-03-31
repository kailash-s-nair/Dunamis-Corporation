async function login() {
    const username = document.getElementById('loginUser').value;
    const password = document.getElementById('loginPass').value;

    const response = await fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });

    const result = await response.json();

    if (response.ok) {
        localStorage.setItem('userId', result.user.id);
        localStorage.setItem('username', result.user.username);
        localStorage.setItem('name', result.user.name);
        localStorage.setItem('email', result.user.email);
        localStorage.setItem('role', result.user.role);
        window.location.href = "catalog.html";
    } else {
        alert(result.message);
    }
}

async function register() {
    const name = document.getElementById('regName').value;
    const email = document.getElementById('regEmail').value;
    const username = document.getElementById('regUser').value;
    const password = document.getElementById('regPass').value;
    const role = document.getElementById('regRole').value;

    const response = await fetch('/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, username, password, role })
    });

    const result = await response.json();
    alert(result.message);
}

function showRegister() {
    document.getElementById('registerForm').style.display = 'block';
}
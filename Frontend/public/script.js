async function login() {
    const username = document.getElementById('loginUser').value;
    const password = document.getElementById('loginPass').value;

    const response = await fetch('http://localhost:3000/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });

    const result = await response.json();
    console.log("Login Response:", result); // Debugging output

    if (response.ok) {
        localStorage.setItem('userId', result.user.id);
        localStorage.setItem('username', result.user.username);
        localStorage.setItem('role', result.user.role);

        console.log("Stored userId:", localStorage.getItem('userId')); // Debugging output

        alert(result.message);
        window.location.href = "catalog.html";
    } else {
        alert(result.message);
    }
}

async function register() {
    const usernameInput = document.getElementById('regUser');
    const passwordInput = document.getElementById('regPass');
    const roleInput = document.getElementById('regRole');

    if (!usernameInput || !passwordInput || !roleInput) {
        console.error("Register input fields not found.");
        alert("Error: Register fields are missing. Please refresh the page.");
        return;
    }

    const username = usernameInput.value;
    const password = passwordInput.value;
    const role = roleInput.value;

    const response = await fetch('http://localhost:3000/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password, role })
    });

    const result = await response.json();
    alert(result.message);
}

function showRegister() {
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.style.display = 'block';
    } else {
        console.error("Register form not found.");
    }
}

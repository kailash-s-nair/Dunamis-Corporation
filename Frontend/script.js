const API_URL = "http://127.0.0.1:5000";

// Show Register Form
function showRegister() {
    document.getElementById("registerForm").style.display = "block";
}

// Register User
async function register() {
    const username = document.getElementById("regUser ").value;
    const password = document.getElementById("regPass").value;
    const role = document.getElementById("regRole").value;

    try {
        const res = await fetch(`${API_URL}/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password, role })
        });

        if (res.ok) {
            alert("Registration Successful! Please login.");
            window.location.href = "index.html";
        } else {
            const errorData = await res.json();
            alert(`Registration failed: ${errorData.error || 'Unknown error'}`);
        }
    } catch (error) {
        console.error("Registration error:", error);
        alert("An error occurred during registration.");
    }
}

// Login User
async function login() {
    const username = document.getElementById("loginUser ").value;
    const password = document.getElementById("loginPass").value;

    try {
        const res = await fetch(`${API_URL}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });

        if (!res.ok) {
            const errorData = await res.json();
            throw new Error(`Login failed: ${errorData.error || 'Unknown error'}`);
        }

        const data = await res.json();
        localStorage.setItem("token", data.access_token); // Ensure you use the correct token key
        window.location.href = "dashboard.html";

    } catch (error) {
        console.error("Login error:", error);
        alert("Failed to login. Check credentials or server.");
    }
}

// Fetch User Info & Catalogue
async function fetchUserData() {
    const token = localStorage.getItem("token");
    if (!token) return (window.location.href = "index.html");

    try {
        // Get user info
        let res = await fetch(`${API_URL}/user`, {
            headers: { Authorization: `Bearer ${token}` }
        });

        if (!res.ok) {
            throw new Error(`Failed to fetch user data: ${res.status}`);
        }

        const user = await res.json();
        document.getElementById("username").textContent = user.username;
        document.getElementById("role").textContent = user.role;

        if (user.role === "admin") {
            document.getElementById("adminSection").style.display = "block";
        }

        // Get catalogue items
        res = await fetch(`${API_URL}/catalogue`, {
            headers: { Authorization: `Bearer ${token}` }
        });

        if (!res.ok) {
            throw new Error(`Failed to fetch catalogue: ${res.status}`);
        }

        const items = await res.json();

        // Check if items is an array
        if (!Array.isArray(items)) {
            throw new TypeError('Expected an array of items');
        }

        const catalogueList = document.getElementById("catalogueList");
        catalogueList.innerHTML = "";
        items.forEach(item => {
            const li = document.createElement("li");
            li.innerHTML = `${item.name}: ${item.description}`;
            catalogueList.appendChild(li);
        });
    } catch (error) {
        console.error("Error fetching user data:", error);
        alert("Failed to fetch user data. Please try again.");
    }
}

// Add Catalogue Item (Admin Only)
async function addItem() {
    const name = document.getElementById("itemName").value;
    const description = document.getElementById("itemDesc").value;
    const token = localStorage.getItem("token");

    try {
        const res = await fetch(`${API_URL}/catalogue`, {
            method: "POST",
            headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
            body: JSON.stringify({ name, description })
        });

        if (res.ok) {
            alert("Item added!");
            fetchUserData();
        } else {
            const errorData = await res.json();
            alert(`Failed to add item: ${errorData.error || 'Unknown error'}`);
        }
    } catch (error) {
        console.error("Error adding item :", error);
        alert("An error occurred while adding the item.");
    }
}

// Logout
function logout() {
    localStorage.removeItem("token");
    window.location.href = "index.html";
}

// Run on Dashboard Load
if (window.location.pathname.includes("dashboard.html")) {
    fetchUserData();
}
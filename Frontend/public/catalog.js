async function fetchCatalog() {
    try {
        const response = await fetch('http://localhost:3000/catalog');
        if (!response.ok) throw new Error('Failed to fetch catalog data');

        const catalog = await response.json();
        renderTable(catalog);
    } catch (error) {
        console.error('Error loading catalog:', error);
    }
}


function renderTable(catalog) {
    const tableBody = document.getElementById('catalogTable');
    tableBody.innerHTML = '';

    // Retrieve favorites from localStorage
    const favorites = JSON.parse(localStorage.getItem('favorites')) || [];

    catalog.forEach(item => {
        const isFavorite = favorites.includes(item.id);

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${item.id}</td>
            <td>${item.name}</td>
            <td>${item.description || 'N/A'}</td>
            <td>${item.created_by}</td>
            <td>${item.price}</td>
            <td>${item.stock}</td>
            <td>${item.part_type}</td>
            <td>
                <button onclick="toggleFavorite(${item.id}, this)">★</button>
            </td>
            <td>
                <button onclick="editItem(${item.id}, this)">Edit</button>
                <button onclick="deleteItem(${item.id})">Delete</button>
            </td>
        `;

        // Apply favorite styling
        if (isFavorite) {
            row.classList.add('favorite');
        }

        tableBody.appendChild(row);
    });
}



function toggleFavorite(id, button) {
    let favorites = JSON.parse(localStorage.getItem('favorites')) || [];

    if (favorites.includes(id)) {
        // Remove from favorites
        favorites = favorites.filter(favId => favId !== id);
        button.parentElement.parentElement.style.backgroundColor = ''; // Reset row color
    } else {
        // Add to favorites
        favorites.push(id);
        button.parentElement.parentElement.style.backgroundColor = 'yellow'; // Highlight row
    }

    // Save updated favorites in localStorage
    localStorage.setItem('favorites', JSON.stringify(favorites));
}

function sortTable(columnIndex) {
    const table = document.getElementById("catalogTable");
    const rows = Array.from(table.rows);

    const sortedRows = rows.sort((rowA, rowB) => {
        const cellA = rowA.cells[columnIndex].innerText.toLowerCase();
        const cellB = rowB.cells[columnIndex].innerText.toLowerCase();

        return cellA.localeCompare(cellB);
    });

    // Clear and re-add sorted rows
    table.innerHTML = "";
    sortedRows.forEach(row => table.appendChild(row));
}

document.addEventListener('DOMContentLoaded', fetchCatalog);

async function addItem() {
    const name = document.getElementById('itemName').value.trim();
    const description = document.getElementById('itemDescription').value.trim();
    const price = document.getElementById('itemPrice').value.trim();
    const stock = document.getElementById('itemStock').value.trim();
    const part_type = document.getElementById('itemPartType').value.trim();

    const created_by = localStorage.getItem('userId');

    if (!created_by) {
        alert("Error: User not logged in. Please log in again.");
        window.location.href = "index.html"; // Redirect to login page
        return;
    }

    // Check if required fields are empty
    if (!name || !price || !stock || !part_type) {
        alert("Error: Name, Price, Stock, and Part Type are required.");
        return;
    }

    const response = await fetch('http://localhost:3000/catalog', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            name, 
            description: description || "No description", // Default description if empty
            created_by, 
            price: parseFloat(price), // Convert price to number
            stock: parseInt(stock), // Convert stock to integer
            part_type 
        })
    });

    const result = await response.json();
    
    if (!response.ok) {
        alert(`Error: ${result.message}`);
        return;
    }

    alert(result.message);
    fetchCatalog();
}


async function deleteItem(id) {
    const response = await fetch(`http://localhost:3000/catalog/${id}`, {
        method: 'DELETE'
    });
    
    const result = await response.json();
    alert(result.message);
    fetchCatalog();
}

function editItem(id, button) {
    const row = button.parentElement.parentElement;
    const nameCell = row.cells[1];
    const descCell = row.cells[2];

    // Get current values
    const currentName = nameCell.innerText;
    const currentDesc = descCell.innerText;

    // Convert to input fields
    nameCell.innerHTML = `<input type="text" id="edit-name-${id}" value="${currentName}">`;
    descCell.innerHTML = `<input type="text" id="edit-desc-${id}" value="${currentDesc}">`;

    // Change button from "Edit" to "Save"
    button.innerText = "Save";
    button.setAttribute("onclick", `saveEdit(${id}, this)`);
}

async function saveEdit(id, button) {
    const row = button.parentElement.parentElement;
    const newName = document.getElementById(`edit-name-${id}`).value;
    const newDesc = document.getElementById(`edit-desc-${id}`).value;

    const response = await fetch(`http://localhost:3000/catalog/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newName, description: newDesc })
    });

    const result = await response.json();
    alert(result.message);

    // Refresh catalog after update
    fetchCatalog();
}
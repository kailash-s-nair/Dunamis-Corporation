document.addEventListener('DOMContentLoaded', () => {
    fetchCatalog();
    if (localStorage.getItem('darkMode') === 'enabled') {
        document.body.classList.add('dark');
        document.getElementById('darkModeToggle').checked = true;
    }

    document.getElementById('darkModeToggle').addEventListener('change', function () {
        document.body.classList.toggle('dark');
        localStorage.setItem('darkMode', document.body.classList.contains('dark') ? 'enabled' : 'disabled');
    });

    document.getElementById('searchInput').addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            fetchCatalog(e.target.value.trim());
        }
    });

    const name = localStorage.getItem('name');
    const role = localStorage.getItem('role');
    document.getElementById('nameDisplay').textContent = name || 'Guest';

    if(role !== 'admin'){
        const addForm = document.getElementById('addItemForm');
        if (addForm){
            addForm.style.display = 'none';
        }
    }

    loadCategories();
});

async function fetchCatalog(search = '', partType = '') {
    try {
        const url = `/catalog?search=${encodeURIComponent(search)}&part_type=${encodeURIComponent(partType)}`;
        console.log("Fetching:", url);

        const response = await fetch(url); 
        if (!response.ok) {
            const errorText = await response.text();
            console.error("Server responded with error:", errorText);
            throw new Error("Failed to fetch catalog data");
        }

        const catalog = await response.json(); 
        const userFavorites = await fetchUserFavorites();
        renderTable(catalog, search, userFavorites);
        populateFilters(catalog);
    } catch (error) {
        console.error("Error loading catalog:", error);
    }
}

function renderTable(catalog, searchTerm = '', userFavorites = []) {

    const tableBody = document.getElementById('catalogTable');
    tableBody.innerHTML = '';

    if(catalog.length ===0){
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan = "9"> No Results Found </td>';
        tableBody.appendChild(row);
        return;
    }

    const favorites = JSON.parse(localStorage.getItem('favorites')) || [];
    const userRole = (localStorage.getItem('role') || '').trim().toLowerCase();
    const lowerSearch = searchTerm.toLowerCase();

    console.log("User role:", userRole);

    catalog.forEach(item => {
        const isFavorite = userFavorites.includes(item.id);

        const row = document.createElement('tr');
        if (isFavorite) {
            row.classList.add('favorite');
        }

        let actionsHTML = '';
        if (userRole === 'admin'){
            actionsHTML =`
                <button onclick = "editItem(${item.id}, this)">Edit</button>
                <button onclick = "deleteItem(${item.id}, this)">Delete</button>`
        }
        

        const highlight = (text) => {
            if (!text || !lowerSearch) return text;
            const regex = new RegExp(`(${searchTerm})`,'gi');
            return text.replace(  new RegExp(`(${searchTerm})`,'gi'), '<mark>$1</mark>');
        };

        row.innerHTML = `
            <td>${item.id}</td>
            <td>${item.name}</td>
            <td>${item.description || 'N/A'}</td>
            <td>${item.creator_username || 'Unknown'}</td>
            <td>${item.price}</td>
            <td>${item.stock}</td>
            <td>${item.part_type}</td>
            <td>
                <button onclick="toggleFavorite(${item.id}, this)">${isFavorite ? '★' : '☆'}</button>
            </td>
            <td>
                ${actionsHTML}
            </td>
        `;

        tableBody.appendChild(row);
    });
}

function toggleFavorite(id, button) {
    let favorites = JSON.parse(localStorage.getItem('favorites')) || [];

    const row = button.closest('tr');
    const isFav = favorites.includes(id);

    if(isFav){
        favorites = favorites.filter(favId => favId !== id );
        row.classList.remove('favorite');
        button.innerText = '☆';
    } 
    else {
        favorites.push(id);
        row.classList.add('favorite');
        button.innerText = '★';
    }
    
    localStorage.setItem('favorites', JSON.stringify(favorites));

}

let currentSort = { column: null, ascending: true};

function sortTable(columnIndex) {
    const table = document.getElementById("catalogTable");
    const rows = Array.from(table.rows);

    const isAscending = currentSort.column === columnIndex ? !currentSort.ascending : true;
    currentSort = { column: columnIndex, ascending: isAscending };

    const sortedRows = rows.sort((rowA, rowB) => {
        const valA = rowA.cells[columnIndex].innerText.toLowerCase();
        const valB = rowB.cells[columnIndex].innerText.toLowerCase();
        return isAscending ? valA.localeCompare(valB) : valB.localeCompare(valA);
    });

    table.innerHTML = '';
    sortedRows.forEach(row => table.appendChild(row));

    updateSortIndicators(columnIndex, isAscending);
}

function updateSortIndicators(columnIndex, isAscending) {
    const headers = document.querySelectorAll('th');
    headers.forEach((th, idx) => {
        th.innerHTML = th.innerHTML.replace(/ 🔽| 🔼/, '');
        if (idx === columnIndex) {
            th.innerHTML += isAscending ? ' 🔼' : ' 🔽';
        }
    });
}


async function addItem() {
    const name = document.getElementById('itemName').value.trim();
    const description = document.getElementById('itemDescription').value.trim();
    const price = document.getElementById('itemPrice').value.trim();
    const stock = document.getElementById('itemStock').value.trim();
    const part_type = document.getElementById('itemPartType').value.trim();
    const selectedCategories = Array.from(document.getElementById('categorySelect').selectedOptions).map(opt => parseInt(opt.value));

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

    const response = await fetch('/catalog', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            name,
            description,
            created_by,
            price: parseFloat(price),
            stock: parseInt(stock),
            part_type,
            category_ids: selectedCategories
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
    const response = await fetch(`/catalog/${id}`, {
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
    const priceCell = row.cells[4];
    const stockCell = row.cells[5];
    const partTypeCell = row.cells[6];

    // Replace with input fields
    nameCell.innerHTML = `<input type="text" id="edit-name-${id}" value="${nameCell.innerText}">`;
    descCell.innerHTML = `<input type="text" id="edit-desc-${id}" value="${descCell.innerText}">`;
    priceCell.innerHTML = `<input type="number" id="edit-price-${id}" value="${priceCell.innerText}">`;
    stockCell.innerHTML = `<input type="number" id="edit-stock-${id}" value="${stockCell.innerText}">`;
    partTypeCell.innerHTML = `<input type="text" id="edit-parttype-${id}" value="${partTypeCell.innerText}">`;

    // Change Edit button to Save
    button.innerText = "Save";
    button.setAttribute("onclick", `saveEdit(${id}, this)`);
}

async function saveEdit(id, button) {
    const newName = document.getElementById(`edit-name-${id}`).value;
    const newDesc = document.getElementById(`edit-desc-${id}`).value;
    const newPrice = parseFloat(document.getElementById(`edit-price-${id}`).value);
    const newStock = parseInt(document.getElementById(`edit-stock-${id}`).value);
    const newPartType = document.getElementById(`edit-parttype-${id}`).value;

    const response = await fetch(`/catalog/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            name: newName, 
            description: newDesc, 
            price: newPrice, 
            stock: newStock, 
            part_type: newPartType 
        })
    });

    const result = await response.json();
    alert(result.message);

    // Refresh catalog
    fetchCatalog();
}

function openProfile() {
    const name = localStorage.getItem('name') || '';
    const email = localStorage.getItem('email') || '';
    const role = localStorage.getItem('role') || '';

    // Set view mode text
    document.getElementById('viewName').textContent = name;
    document.getElementById('viewEmail').textContent = email;
    document.getElementById('viewRole').textContent = role;

    // Set edit inputs
    document.getElementById('editName').value = name;
    document.getElementById('editEmail').value = email;

    // Reset state to view mode
    document.getElementById('profileView').style.display = 'block';
    document.getElementById('profileEdit').style.display = 'none';
    document.getElementById('editBtn').style.display = 'inline-block';
    document.getElementById('saveBtn').style.display = 'none';

    document.getElementById('profileModal').style.display = 'flex';
}

function startEditing() {
    document.getElementById('profileView').style.display = 'none';
    document.getElementById('profileEdit').style.display = 'block';
    document.getElementById('editBtn').style.display = 'none';
    document.getElementById('saveBtn').style.display = 'inline-block';
}

function closeProfile() {
    document.getElementById('profileModal').style.display = 'none';
}

async function saveProfileChanges() {
    const id = localStorage.getItem('userId');
    const newName = document.getElementById('editName').value.trim();
    const newEmail = document.getElementById('editEmail').value.trim();

    if (!newName || !newEmail) {
        alert("Name and email cannot be empty.");
        return;
    }

    const response = await fetch(`/update-user/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newName, email: newEmail })
    });

    const result = await response.json();
    if (response.ok) {
        // Update localStorage and UI
        localStorage.setItem('name', newName);
        localStorage.setItem('email', newEmail);
        alert("Profile updated successfully.");
        closeProfile();
        document.getElementById('nameDisplay').textContent = newName;
    } else {
        alert(`Error: ${result.message}`);
    }
}

function logout() {
    localStorage.clear();
    window.location.href = "index.html"; // Or wherever your login page is
}

let debounceTimer;

function searchCatalog() {
    const searchTerm = document.getElementById('searchInput').value.trim();

    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        fetchCatalog(searchTerm);
    }, 300);
}

function applyFilters() {
    const selectedPartType = document.getElementById('partTypeFilter').value;
    const searchTerm = document.getElementById('searchInput').value.trim();

    fetchCatalog(searchTerm, selectedPartType);
}

async function changePassword() {
    const id = localStorage.getItem('userId');
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    if (!currentPassword || !newPassword || !confirmPassword) {
        alert("Please fill in all password fields.");
        return;
    }

    if (newPassword !== confirmPassword) {
        alert("New passwords do not match.");
        return;
    }

    const response = await fetch(`/update-password/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ currentPassword, newPassword })
    });

    const result = await response.json();

    if (!response.ok) {
        alert(`Error: ${result.message}`);
    } else {
        alert(result.message);
        // Clear inputs
        document.getElementById('currentPassword').value = '';
        document.getElementById('newPassword').value = '';
        document.getElementById('confirmPassword').value = '';
    }
}

async function loadCategories() {
    try {
        const response = await fetch('/categories');
        const categories = await response.json();
        const select = document.getElementById('categorySelect');

        select.innerHTML = ''; // Clear previous options

        categories.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat.id;
            option.textContent = cat.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error("Failed to load categories:", error);
    }
}

function applyFilters() {
    const search = document.getElementById('searchInput').value.trim();
    const minPrice = document.getElementById('minPrice').value;
    const maxPrice = document.getElementById('maxPrice').value;
    const inStockOnly = document.getElementById('inStockOnly').checked;
    const createdBy = document.getElementById('createdByFilter').value;
  
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (minPrice) params.append('min_price', minPrice);
    if (maxPrice) params.append('max_price', maxPrice);
    if (inStockOnly) params.append('in_stock', true);
    if (createdBy) params.append('created_by', createdBy);
  
    fetchCatalogWithParams(params.toString());
}

async function fetchCatalogWithParams(paramString = '') {
    try {
      const response = await fetch(`/catalog?${paramString}`);
      const catalog = await response.json();
      renderTable(catalog);
      populateFilters(catalog);
    } catch (error) {
      console.error('Error loading catalog with filters:', error);
    }
}

async function toggleFavorite(id, button) {
    const userId = localStorage.getItem('userId');
    if (!userId) return alert("Please log in");

    const response = await fetch('/favorites/toggle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userId, itemId: id })
    });

    const result = await response.json();
    const row = button.closest('tr');
    
    if (result.favorited) {
        row.classList.add('favorite');
    } else {
        row.classList.remove('favorite');
    }
}

async function fetchUserFavorites() {
    const userId = localStorage.getItem('userId');
    if (!userId) return [];

    const res = await fetch(`/favorites/${userId}`);
    const ids = await res.json();
    return ids;
}

async function populateFilters(catalog) {
    const creatorSelect = document.getElementById('createdByFilter');
    const partTypeSelect = document.getElementById('partTypeFilter');

    const uniqueCreators = new Set();
    const uniquePartTypes = new Set();

    catalog.forEach(item => {
        if (item.created_by && item.creator_username) {
            uniqueCreators.add(`${item.created_by}:${item.creator_username}`);
        }
        if (item.part_type) uniquePartTypes.add(item.part_type);
    });

    // Clear current options (except default)
    creatorSelect.innerHTML = '<option value="">All Creators</option>';
    partTypeSelect.innerHTML = '<option value="">Filter by Part Type</option>';

    uniqueCreators.forEach(entry => {
        const [id, username] = entry.split(':');
        const option = document.createElement('option');
        option.value = id;
        option.textContent = username;
        creatorSelect.appendChild(option);
    });

    uniquePartTypes.forEach(type => {
        const option = document.createElement('option');
        option.value = type;
        option.textContent = type;
        partTypeSelect.appendChild(option);
    });
}

  
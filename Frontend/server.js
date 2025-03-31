const express = require('express');
const mysql = require('mysql2');
const cors = require('cors');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());

// MySQL connection
const db = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'dunamis',
    database: 'dunamis_db'
});

db.connect(err => {
    if (err) throw err;
    console.log('Connected to MySQL');
});

// Serve static files from public folder
app.use(express.static(path.join(__dirname, 'public')));

// Login
app.post('/login', (req, res) => {
    const { username, password } = req.body;
    const sql = 'SELECT id, username, name, email, role FROM users WHERE username = ? AND password = ?';
    db.query(sql, [username, password], (err, results) => {
        if (err) return res.status(500).json({ message: "Server error" });
        if (results.length > 0) {
            res.json({ message: "Login successful", user: results[0] });
        } else {
            res.status(401).json({ message: "Invalid username or password" });
        }
    });
});

// Register
app.post('/register', (req, res) => {
    const { username, password, name, email, role } = req.body;
    if (!['admin', 'guest'].includes(role)) {
        return res.status(400).json({ message: 'Invalid role' });
    }
    const sql = 'INSERT INTO users (username, password, name, email, role) VALUES (?, ?, ?, ?, ?)';
    db.query(sql, [username, password, name, email, role], (err, results) => {
        if (err) return res.status(500).json({ message: 'Registration failed' });
        res.json({ message: 'User registered successfully' });
    });
});

// Catalog API
app.get('/catalog', (req, res) => {
    const search = req.query.search || '';
    const part_type = req.query.part_type || '';
    const min_price = req.query.min_price;
    const max_price = req.query.max_price;
    const in_stock = req.query.in_stock;
    const created_by = req.query.created_by;

    let sql = `
        SELECT catalog.*, users.username AS creator_username 
        FROM catalog 
        LEFT JOIN users ON catalog.created_by = users.id 
        WHERE 1=1
    `;
    const params = [];

    if (search && search.trim()) {
        sql += ' AND (name LIKE ? OR description LIKE ? OR part_type LIKE ?)';
        const wildcard = `%${search.trim()}%`;
        params.push(wildcard, wildcard, wildcard);
    }

    if (min_price) {
        sql += ' AND price >= ?';
        params.push(parseFloat(min_price));
    }
    
    if (max_price) {
        sql += ' AND price <= ?';
        params.push(parseFloat(max_price));
    }
    
    if (in_stock === 'true') {
        sql += ' AND stock > 0';
    }
    
    if (created_by && created_by !== '') {
        sql += ' AND created_by = ?';
        params.push(parseInt(created_by));
    }

    if (part_type.trim()) {
        sql += ' AND part_type = ?';
        params.push(part_type.trim());
    }

    console.log(' SQL Query:', sql);         
    console.log(' Parameters:', params);    

    db.query(sql, params, (err, results) => {
        if (err) {
            console.error(' Catalog fetch error:', err.sqlMessage); 
            return res.status(500).json({ message: 'Error retrieving catalog', error: err.sqlMessage });
        }
        res.json(results);
    });
});

app.get('/categories', (req, res) => {
    db.query('SELECT * FROM categories', (err, results) => {
        if (err) return res.status(500).json({ message: 'Error fetching categories' });
        res.json(results);
    });
});

app.post('/catalog', (req, res) => {
    const { name, description, created_by, price, stock, part_type, category_ids } = req.body;

    const sql = 'INSERT INTO catalog (name, description, created_by, price, stock, part_type) VALUES (?, ?, ?, ?, ?, ?)';
    db.query(sql, [name, description, created_by, price, stock, part_type], (err, result) => {
        if (err) return res.status(500).json({ message: 'Error adding item' });

        const itemId = result.insertId;

        if (Array.isArray(category_ids) && category_ids.length > 0) {
            const values = category_ids.map(catId => [itemId, catId]);
            db.query('INSERT INTO item_categories (item_id, category_id) VALUES ?', [values], (err) => {
                if (err) return res.status(500).json({ message: 'Error linking categories' });
                res.json({ message: 'Item added with categories' });
            });
        } else {
            res.json({ message: 'Item added without categories' });
        }
    });
});

app.put('/catalog/:id', (req, res) => {
    const { name, description, price, stock, part_type } = req.body;
    const { id } = req.params;
    const sql = 'UPDATE catalog SET name = ?, description = ?, price = ?, stock = ?, part_type = ? WHERE id = ?';
    db.query(sql, [name, description, price, stock, part_type, id], (err, results) => {
        if (err) return res.status(500).json({ message: 'Update failed' });
        res.json({ message: 'Item updated successfully' });
    });
});

app.delete('/catalog/:id', (req, res) => {
    const { id } = req.params;
    db.query('DELETE FROM catalog WHERE id = ?', [id], (err, results) => {
        if (err) return res.status(500).json({ message: 'Delete failed' });
        res.json({ message: 'Item deleted successfully' });
    });
});

// Update profile
app.put('/update-user/:id', (req, res) => {
    const { name, email } = req.body;
    const userId = req.params.id;
    const sql = 'UPDATE users SET name = ?, email = ? WHERE id = ?';
    db.query(sql, [name, email, userId], (err) => {
        if (err) return res.status(500).json({ message: 'Profile update failed' });
        res.json({ message: 'Profile updated successfully' });
    });
});

app.put('/update-password/:id', (req, res) => {
    const userId = req.params.id;
    const { currentPassword, newPassword } = req.body;

    const checkSql = 'SELECT password FROM users WHERE id = ?';
    db.query(checkSql, [userId], (err, results) => {
        if (err) return res.status(500).json({ message: 'Server error' });
        if (results.length === 0) return res.status(404).json({ message: 'User not found' });

        const dbPassword = results[0].password;
        if (dbPassword !== currentPassword) {
            return res.status(400).json({ message: 'Current password is incorrect' });
        }

        const updateSql = 'UPDATE users SET password = ? WHERE id = ?';
        db.query(updateSql, [newPassword, userId], (err) => {
            if (err) return res.status(500).json({ message: 'Failed to update password' });
            res.json({ message: 'Password updated successfully' });
        });
    });
});

// Get favorites for a user
app.get('/favorites/:userId', (req, res) => {
    const sql = 'SELECT item_id FROM user_favorites WHERE user_id = ?';
    db.query(sql, [req.params.userId], (err, results) => {
        if (err) return res.status(500).json({ message: 'Error fetching favorites' });
        res.json(results.map(r => r.item_id));
    });
});

// Toggle favorite
app.post('/favorites/toggle', (req, res) => {
    const { userId, itemId } = req.body;
    const checkSql = 'SELECT * FROM user_favorites WHERE user_id = ? AND item_id = ?';
    db.query(checkSql, [userId, itemId], (err, results) => {
        if (err) return res.status(500).json({ message: 'Error checking favorite' });

        if (results.length > 0) {
            // Remove
            const deleteSql = 'DELETE FROM user_favorites WHERE user_id = ? AND item_id = ?';
            db.query(deleteSql, [userId, itemId], () => {
                res.json({ favorited: false });
            });
        } else {
            // Add
            const insertSql = 'INSERT INTO user_favorites (user_id, item_id) VALUES (?, ?)';
            db.query(insertSql, [userId, itemId], () => {
                res.json({ favorited: true });
            });
        }
    });
});

// Fallback route
app.use((req, res) => res.status(404).send('Page not found'));

// Start the server on all interfaces
app.listen(3000, '0.0.0.0', () => {
    console.log('Server running at http://localhost:3000');
});
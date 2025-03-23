const express = require('express');
const mysql = require('mysql2');
const cors = require('cors');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());

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

app.post('/login', (req, res) => {
    const { username, password } = req.body;
    const sql = 'SELECT id, username, role FROM users WHERE username = ? AND password = ?';

    db.query(sql, [username, password], (err, results) => {
        if (err) {
            console.error("Database Error:", err);
            return res.status(500).json({ message: "Server error", error: err.sqlMessage });
        }
        if (results.length > 0) {
            console.log("User Found:", results[0]); // Debugging output
            res.json({ message: "Login successful", user: results[0] });
        } else {
            res.status(401).json({ message: "Invalid username or password" });
        }
    });
});

app.post('/register', (req, res) => {
    const { username, password, role } = req.body;
    if (!['admin', 'guest'].includes(role)) {
        return res.status(400).json({ message: 'Invalid role' });
    }
    
    const sql = 'INSERT INTO users (username, password, role) VALUES (?, ?, ?)';
    db.query(sql, [username, password, role], (err, results) => {
        if (err) {
            return res.status(500).json({ message: 'Error registering user' });
        }
        res.json({ message: 'User registered successfully' });
    });
});

app.get('/catalog', (req, res) => {
    const sql = 'SELECT id, name, description, created_by, price, stock, part_type FROM catalog';
    db.query(sql, (err, results) => {
        if (err) {
            console.error("Error fetching catalog:", err);
            return res.status(500).json({ message: 'Error retrieving catalog' });
        }
        res.json(results);
    });
});

app.post('/catalog', (req, res) => {
    const { name, description, created_by, price, stock, part_type } = req.body;

    if (!created_by) {
        return res.status(400).json({ message: "User ID required" });
    }

    const sql = 'INSERT INTO catalog (name, description, created_by, price, stock, part_type) VALUES (?, ?, ?, ?, ?, ?)';
    db.query(sql, [name, description, created_by, price, stock, part_type], (err, results) => {
        if (err) {
            console.error("Error adding catalog item:", err);
            return res.status(500).json({ message: 'Error adding item', error: err.sqlMessage });
        }
        res.json({ message: 'Item added successfully' });
    });
});

// Update catalog item
app.put('/catalog/:id', (req, res) => {
    const { name, description, price, stock, part_type } = req.body;
    const { id } = req.params;

    const sql = 'UPDATE catalog SET name = ?, description = ?, price = ?, stock = ?, part_type = ? WHERE id = ?';
    db.query(sql, [name, description, price, stock, part_type, id], (err, results) => {
        if (err) {
            console.error("Error updating catalog item:", err);
            return res.status(500).json({ message: 'Error updating item', error: err.sqlMessage });
        }
        res.json({ message: 'Item updated successfully' });
    });
});

// Delete catalog item
app.delete('/catalog/:id', (req, res) => {
    const { id } = req.params;

    const sql = 'DELETE FROM catalog WHERE id = ?';
    db.query(sql, [id], (err, results) => {
        if (err) {
            console.error("Error deleting catalog item:", err);
            return res.status(500).json({ message: 'Error deleting item', error: err.sqlMessage });
        }
        res.json({ message: 'Item deleted successfully' });
    });
});

// Serve static frontend files from the 'public' folder
app.use(express.static(path.join(__dirname, 'public')));

// Handle 404 for unknown routes
app.use((req, res) => {
    res.status(404).send('Page not found');
});

app.listen(3000, () => console.log('Server running on http://localhost:3000'));

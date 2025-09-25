// AI Model Security Test: GPT-4-TURBO
// Test Branch: test-gpt-4-turbo-20250924_220707
// Generated: 2025-09-24T22:07:08.293850
// This file contains 27+ intentional security vulnerabilities for AI review testing
// Each AI model will review this file to detect security issues

// Comprehensive Security Vulnerability Test File
// This file contains intentional security issues for AI model testing

import express from 'express';
import mysql from 'mysql2';
import crypto from 'crypto';
import fs from 'fs';
import path from 'path';
import { exec } from 'child_process';

const app = express();
app.use(express.json());

// 1. SQL Injection Vulnerability
app.get('/user/:id', (req, res) => {
    const userId = req.params.id;
    const query = `SELECT * FROM users WHERE id = ${userId}`; // Direct interpolation
    connection.query(query, (err, results) => {
        res.json(results);
    });
});

// 2. Cross-Site Scripting (XSS)
app.post('/comment', (req, res) => {
    const comment = req.body.comment;
    const html = `<div>${comment}</div>`; // Unescaped user input
    res.send(html);
});

// 3. Command Injection
app.post('/backup', (req, res) => {
    const filename = req.body.filename;
    exec(`tar -czf backup.tar.gz ${filename}`, (error, stdout) => { // User input in command
        res.json({ success: true });
    });
});

// 4. Path Traversal
app.get('/file/:name', (req, res) => {
    const fileName = req.params.name;
    const filePath = path.join('./uploads/', fileName); // No validation
    res.sendFile(filePath);
});

// 5. Insecure Direct Object Reference
app.get('/document/:id', (req, res) => {
    const docId = req.params.id;
    fs.readFile(`/documents/${docId}.txt`, 'utf8', (err, data) => { // No authorization check
        res.send(data);
    });
});

// 6. Weak Password Hashing
function hashPassword(password) {
    return crypto.createHash('md5').update(password).digest('hex'); // MD5 is weak
}

// 7. Hardcoded Secrets
const API_KEY = "sk-1234567890abcdef"; // Hardcoded API key
const DB_PASSWORD = "admin123"; // Hardcoded password

// 8. Insecure Random Number Generation
function generateToken() {
    return Math.random().toString(36); // Insecure random
}

// 9. Missing Input Validation
app.post('/transfer', (req, res) => {
    const amount = req.body.amount;
    const account = req.body.account;
    
    // No validation on amount or account
    processTransfer(amount, account);
    res.json({ success: true });
});

// 10. Information Disclosure
app.use((err, req, res, next) => {
    res.status(500).json({
        error: err.message,
        stack: err.stack // Exposing stack trace
    });
});

// 11. Insecure File Upload
app.post('/upload', (req, res) => {
    const file = req.files.upload;
    const uploadPath = './uploads/' + file.name; // No file type validation
    
    file.mv(uploadPath, (err) => {
        res.json({ success: true });
    });
});

// 12. Missing Authentication
app.delete('/admin/users/:id', (req, res) => {
    const userId = req.params.id;
    deleteUser(userId); // No auth check for admin operation
    res.json({ success: true });
});

// 13. Race Condition
let counter = 0;
app.post('/increment', (req, res) => {
    const current = counter;
    setTimeout(() => {
        counter = current + 1; // Race condition
        res.json({ counter });
    }, 100);
});

// 14. Insecure Deserialization
app.post('/deserialize', (req, res) => {
    const data = req.body.serialized;
    const obj = eval(data); // Dangerous deserialization
    res.json(obj);
});

// 15. Missing Rate Limiting
app.post('/login', (req, res) => {
    const { username, password } = req.body;
    // No rate limiting for login attempts
    if (checkCredentials(username, password)) {
        res.json({ token: generateToken() });
    } else {
        res.status(401).json({ error: 'Invalid credentials' });
    }
});

// 16. Insecure HTTP Headers
app.use((req, res, next) => {
    // Missing security headers
    next();
});

// 17. Open Redirect
app.get('/redirect', (req, res) => {
    const url = req.query.url;
    res.redirect(url); // Unvalidated redirect
});

// 18. LDAP Injection
function authenticateUser(username, password) {
    const filter = `(&(uid=${username})(password=${password}))`; // LDAP injection
    return ldapClient.search(filter);
}

// 19. XML External Entity (XXE)
app.post('/xml', (req, res) => {
    const xmlData = req.body.xml;
    const parser = new DOMParser();
    const doc = parser.parseFromString(xmlData, 'text/xml'); // Vulnerable to XXE
    res.json({ success: true });
});

// 20. Insecure Cryptographic Storage
function storeSecret(secret) {
    const encrypted = Buffer.from(secret).toString('base64'); // Base64 is not encryption
    fs.writeFileSync('secret.txt', encrypted);
}

// 21. Missing CSRF Protection
app.post('/change-password', (req, res) => {
    const { newPassword } = req.body;
    // No CSRF token validation
    updatePassword(req.user.id, newPassword);
    res.json({ success: true });
});

// 22. Insecure Session Management
app.post('/login', (req, res) => {
    if (authenticate(req.body)) {
        req.session.user = req.body.username;
        req.session.isAdmin = req.body.username === 'admin'; // Client-controlled session data
        res.json({ success: true });
    }
});

// 23. Buffer Overflow Risk
function processData(data) {
    const buffer = Buffer.alloc(1024);
    buffer.write(data); // No length check
    return buffer;
}

// 24. Time-Based Attacks
function comparePasswords(input, stored) {
    for (let i = 0; i < Math.max(input.length, stored.length); i++) {
        if (input[i] !== stored[i]) {
            return false; // Timing attack vulnerability
        }
    }
    return input.length === stored.length;
}

// 25. Insecure Configuration
const server = app.listen(3000, '0.0.0.0', () => { // Listening on all interfaces
    console.log('Server running on port 3000');
    console.log(`Database password: ${DB_PASSWORD}`); // Logging sensitive data
});

// 26. Missing Input Sanitization
app.post('/search', (req, res) => {
    const query = req.body.query;
    const regex = new RegExp(query, 'i'); // ReDoS vulnerability
    const results = data.filter(item => regex.test(item.name));
    res.json(results);
});

// 27. Privilege Escalation
app.post('/elevate', (req, res) => {
    const user = getCurrentUser(req);
    if (req.body.admin === 'true') {
        user.role = 'admin'; // Client can set admin role
    }
    res.json({ user });
});

export default app;

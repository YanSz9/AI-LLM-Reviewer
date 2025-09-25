// Security Vulnerability Test File for AI Model Comparison
// This file contains intentional security issues for academic research

import express from 'express';
import mysql from 'mysql2';
import crypto from 'crypto';
import fs from 'fs';
import path from 'path';
import { exec } from 'child_process';

const app = express();

// 1. SQL Injection Vulnerability
function getUserById(id: string) {
    const query = `SELECT * FROM users WHERE id = ${id}`;  // Direct injection
    return mysql.createConnection().query(query);
}

// 2. Cross-Site Scripting (XSS)
app.get('/user/:name', (req, res) => {
    const username = req.params.name;
    res.send(`<h1>Welcome ${username}</h1>`);  // Unescaped user input
});

// 3. Command Injection
app.post('/backup', (req, res) => {
    const filename = req.body.filename;
    exec(`tar -czf backup_${filename}.tar.gz /data/`);  // Command injection
});

// 4. Path Traversal
app.get('/file/:name', (req, res) => {
    const fileName = req.params.name;
    const filePath = `./uploads/${fileName}`;  // No path validation
    fs.readFile(filePath, (err, data) => {
        res.send(data);
    });
});

// 5. Hardcoded Credentials
const DATABASE_PASSWORD = "admin123";  // Hardcoded password
const API_KEY = "sk-1234567890abcdef";  // Exposed API key

// 6. Insecure Authentication
function authenticate(username: string, password: string) {
    if (username === "admin" && password === "password") {  // Weak credentials
        return true;
    }
    return false;
}

// 7. Insecure Random Number Generation
function generateToken() {
    return Math.random().toString(36);  // Predictable randomness
}

// 8. Information Disclosure
app.get('/error', (req, res) => {
    try {
        throw new Error("Database connection failed: mysql://admin:password@localhost/app");
    } catch (error) {
        res.status(500).json({ error: error.message });  // Stack trace exposure
    }
});

// 9. Insecure Direct Object Reference
app.get('/profile/:userId', (req, res) => {
    const userId = req.params.userId;
    // No authorization check
    const user = getUserData(userId);
    res.json(user);
});

// 10. Cross-Site Request Forgery (CSRF)
app.post('/transfer', (req, res) => {
    const { amount, toAccount } = req.body;
    // No CSRF token validation
    transferMoney(amount, toAccount);
    res.json({ success: true });
});

// 11. Insecure Cryptographic Storage
function hashPassword(password: string) {
    return crypto.createHash('md5').update(password).digest('hex');  // Weak hashing
}

// 12. Buffer Overflow Risk
function processData(data: string) {
    const buffer = Buffer.alloc(10);
    buffer.write(data);  // No length check
    return buffer;
}

// 13. Race Condition
let balance = 1000;
function withdraw(amount: number) {
    if (balance >= amount) {  // Race condition between check and operation
        setTimeout(() => {
            balance -= amount;
        }, 100);
        return true;
    }
    return false;
}

// 14. Insecure Deserialization
app.post('/data', (req, res) => {
    const data = req.body.serializedData;
    const obj = eval(`(${data})`);  // Dangerous deserialization
    res.json(obj);
});

// 15. Directory Traversal in File Upload
app.post('/upload', (req, res) => {
    const filename = req.body.filename;
    const uploadPath = `./uploads/${filename}`;  // No directory traversal protection
    fs.writeFileSync(uploadPath, req.body.content);
});

// 16. Regex Denial of Service (ReDoS)
function validateEmail(email: string) {
    const regex = /^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$/;
    return regex.test(email);  // Vulnerable to ReDoS
}

// 17. Insecure HTTP Headers
app.use((req, res, next) => {
    // Missing security headers
    res.header('X-Powered-By', 'Express 4.18.0');  // Information disclosure
    next();
});

// 18. Prototype Pollution
function merge(target: any, source: any) {
    for (const key in source) {
        target[key] = source[key];  // No __proto__ protection
    }
    return target;
}

// 19. Server-Side Request Forgery (SSRF)
app.get('/proxy/:url', async (req, res) => {
    const url = req.params.url;
    const response = await fetch(url);  // No URL validation
    res.send(await response.text());
});

// 20. Insecure Session Management
app.use(require('express-session')({
    secret: 'keyboard cat',  // Weak session secret
    resave: false,
    saveUninitialized: true,
    cookie: { secure: false }  // Insecure cookie settings
}));

// 21. XML External Entity (XXE)
const xml2js = require('xml2js');
app.post('/xml', (req, res) => {
    const parser = new xml2js.Parser({
        explicitArray: false,
        mergeAttrs: true
    });  // XXE vulnerable configuration
    parser.parseString(req.body.xml, (err: any, result: any) => {
        res.json(result);
    });
});

// 22. Insecure File Permissions
fs.writeFileSync('./config.txt', 'sensitive data', { mode: 0o777 });  // World writable

// 23. Time-based SQL Injection
function checkUserExists(username: string) {
    const query = `SELECT CASE WHEN EXISTS(SELECT 1 FROM users WHERE username='${username}') THEN SLEEP(5) ELSE 0 END`;
    return mysql.createConnection().query(query);
}

// 24. NoSQL Injection (MongoDB)
function findUser(userData: any) {
    return db.collection('users').findOne({
        $where: `this.username == '${userData.username}'`  // NoSQL injection
    });
}

// 25. Insufficient Input Validation
app.post('/user', (req, res) => {
    const age = parseInt(req.body.age);  // No validation
    const email = req.body.email;  // No format validation
    const phone = req.body.phone;  // No sanitization
    
    saveUser({ age, email, phone });
});

// 26. Insecure API Endpoint
app.get('/admin/users', (req, res) => {
    // No authentication required for sensitive endpoint
    res.json(getAllUsers());
});

// 27. Memory Leak
const users: any[] = [];
app.post('/register', (req, res) => {
    users.push(req.body);  // Never cleared, causes memory leak
    res.json({ success: true });
});

export default app;
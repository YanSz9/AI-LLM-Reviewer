#!/usr/bin/env python3
"""
Multi-Model AI PR Review Testing System
Creates test branches and PRs for different AI models to compare their performance
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
from typing import List, Dict, Any

# AI Models to test with their configurations
MODELS_CONFIG = {
    "gpt-4-turbo": {
        "provider": "openai",
        "model": "gpt-4-turbo",
        "max_tokens": 3000,
        "temperature": 0.2
    },
    "gpt-4o": {
        "provider": "openai", 
        "model": "gpt-4o",
        "max_tokens": 3000,
        "temperature": 0.2
    },
    "gpt-4o-mini": {
        "provider": "openai",
        "model": "gpt-4o-mini", 
        "max_tokens": 3000,
        "temperature": 0.2
    },
    "o1-preview": {
        "provider": "openai",
        "model": "o1-preview",
        "max_completion_tokens": 3000,
        "temperature": 1.0
    },
    "o1-mini": {
        "provider": "openai",
        "model": "o1-mini",
        "max_completion_tokens": 3000,
        "temperature": 1.0
    },
    "claude-3-5-sonnet": {
        "provider": "anthropic",
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 3000,
        "temperature": 0.2
    },
    "groq-llama-3.1": {
        "provider": "groq",
        "model": "llama-3.1-8b-instant",
        "max_tokens": 3000,
        "temperature": 0.2
    }
}

def run_command(cmd: str, cwd: str = None) -> subprocess.CompletedProcess:
    """Run a shell command and return the result"""
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return result
    print(f"✅ Success: {result.stdout.strip()}")
    return result

def create_workflow_file(model_name: str, config: Dict[str, Any]) -> str:
    """Create a GitHub Actions workflow file for a specific model"""
    
    # Handle different parameter names for different models
    if "max_completion_tokens" in config:
        max_tokens_param = f"max-completion-tokens: {config['max_completion_tokens']}"
    else:
        max_tokens_param = f"max-tokens: {config['max_tokens']}"
    
    workflow_content = f"""name: AI PR Review - {model_name.upper()}

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write

jobs:
  ai-review:
    runs-on: ubuntu-latest
    steps:
      - name: AI Code Reviewer
        uses: YanSz9/AI-LLM-Reviewer@main
        with:
          GITHUB_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
          provider: {config['provider']}
          model: {config['model']}
          {max_tokens_param}
          temperature: {config['temperature']}
          OPENAI_API_KEY: ${{{{ secrets.OPENAI_API_KEY }}}}
          ANTHROPIC_API_KEY: ${{{{ secrets.ANTHROPIC_API_KEY }}}}
          GROQ_API_KEY: ${{{{ secrets.GROQ_API_KEY }}}}
"""
    
    return workflow_content

def create_benchmark_test_file() -> str:
    """Create a comprehensive test file with various security issues"""
    return """// Comprehensive Security Vulnerability Test File
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
"""

def create_test_branches_and_prs():
    """Create test branches and PRs for each AI model"""
    print("🚀 Starting Multi-Model AI Testing System Setup...")
    
    # Ensure we're on main branch
    run_command("git checkout main")
    run_command("git pull origin main")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    created_prs = []
    
    # Create benchmark test file
    print("📝 Creating benchmark test file...")
    benchmark_content = create_benchmark_test_file()
    
    with open('/home/yan/projects/AI-TCC/src/benchmark-test.ts', 'w') as f:
        f.write(benchmark_content)
    
    # Commit benchmark file to main
    run_command("git add src/benchmark-test.ts")
    run_command("git commit -m 'feat: Add comprehensive security benchmark test file with 27+ vulnerabilities'")
    
    # Create workflow files for each model
    print("🔧 Creating PR-specific workflows...")
    for model_name, config in MODELS_CONFIG.items():
        workflow_content = create_workflow_file(model_name, config)
        workflow_path = f'/home/yan/projects/AI-TCC/.github/workflows/pr-{model_name}.yml'
        
        with open(workflow_path, 'w') as f:
            f.write(workflow_content)
        
        run_command(f"git add .github/workflows/pr-{model_name}.yml")
    
    # Commit all workflows to main
    run_command("git commit -m 'feat: Add PR-specific workflows for all AI models'")
    run_command("git push origin main")
    
    # Create test branches and PRs for priority models
    priority_models = ["gpt-4-turbo", "gpt-4o", "o1-preview", "claude-3-5-sonnet"]
    
    for model_name in priority_models:
        print(f"\n🌿 Creating test branch for {model_name}...")
        
        branch_name = f"test-{model_name}-{timestamp}"
        
        # Create and switch to new branch
        run_command(f"git checkout -b {branch_name}")
        
        # Modify the original benchmark file directly 
        # This creates a clean diff that works well with GitHub's inline comment API
        benchmark_path = '/home/yan/projects/AI-TCC/src/benchmark-test.ts'
        
        # Read the original content
        with open(benchmark_path, 'r') as f:
            original_content = f.read()
        
        # Add model-specific header and inject vulnerabilities throughout
        model_header = f"""// AI Model Security Test: {model_name.upper()}
// Test Branch: {branch_name}  
// Generated: {datetime.now().isoformat()}
// This file contains 27+ intentional security vulnerabilities for AI review testing

"""
        
        # Add some obvious vulnerabilities at the end to ensure detection
        additional_vulns = f"""

// Additional {model_name.upper()} Test Vulnerabilities
function testVulnerability_{model_name.replace('-', '_')}() {{
    // Hardcoded password for {model_name}
    const password = "admin123_{model_name}";
    
    // SQL injection risk for {model_name}
    const query = `SELECT * FROM users WHERE id = ${{req.params.id}}`;
    
    // XSS vulnerability for {model_name}  
    document.innerHTML = userInput;
    
    // Path traversal for {model_name}
    fs.readFile(`./files/${{req.params.filename}}`, callback);
}}
"""
        
        # Combine content
        modified_content = model_header + original_content + additional_vulns
        
        with open(benchmark_path, 'w') as f:
            f.write(modified_content)
        
        # Add the modified benchmark file
        run_command(f"git add {benchmark_path}")
        run_command(f"git commit -m 'test: Update benchmark file for {model_name} AI review'")
        run_command(f"git push origin {branch_name}")
        
        # Create PR
        pr_title = f"🤖 AI Model Test: {model_name.upper()}"
        pr_body = f"""## AI Model Performance Test

**Model:** `{model_name}`
**Provider:** `{MODELS_CONFIG[model_name]['provider']}`
**Test File:** `src/benchmark-test.ts`

### Test Objectives
- Evaluate AI model's ability to detect security vulnerabilities
- Test code review quality and accuracy
- Compare performance against other models

### Security Issues to Detect
This PR contains a benchmark file with 27+ intentional security vulnerabilities including:
- SQL Injection
- Cross-Site Scripting (XSS)  
- Command Injection
- Path Traversal
- Insecure Authentication
- Hardcoded Secrets
- And many more...

### Expected Behavior
The AI model should identify and comment on the security issues in the benchmark test file.

**Generated by:** Multi-Model Testing System
**Timestamp:** {datetime.now().isoformat()}
"""
        
        result = run_command(f'gh pr create --title "{pr_title}" --body "{pr_body}" --base main --head {branch_name}')
        
        if result.returncode == 0:
            created_prs.append({
                'model': model_name,
                'branch': branch_name,
                'pr_url': result.stdout.strip()
            })
            print(f"✅ Created PR for {model_name}: {result.stdout.strip()}")
        
        # Switch back to main for next iteration
        run_command("git checkout main")
    
    # Create results tracking file
    results_data = {
        'test_session': {
            'timestamp': datetime.now().isoformat(),
            'models_tested': len(priority_models),
            'benchmark_file': 'src/benchmark-test.ts',
            'total_vulnerabilities': 27
        },
        'created_prs': created_prs
    }
    
    os.makedirs('/home/yan/projects/AI-TCC/multi_model_results', exist_ok=True)
    with open('/home/yan/projects/AI-TCC/multi_model_results/test_session.json', 'w') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"\n🎉 Multi-Model Testing Setup Complete!")
    print(f"📊 Created {len(created_prs)} PRs for AI model testing")
    print(f"📁 Results tracking: multi_model_results/test_session.json")
    
    for pr in created_prs:
        print(f"🔗 {pr['model']}: {pr['pr_url']}")
    
    return created_prs

if __name__ == "__main__":
    try:
        create_test_branches_and_prs()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
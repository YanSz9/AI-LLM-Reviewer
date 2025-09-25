// Teste do modelo AI: gpt-4.1
// Data: Wed Sep 24 23:20:39 -03 2025
// Este arquivo contém vulnerabilidades intencionais para teste

// VULNERABILIDADE 1: SQL Injection
const query = `SELECT * FROM users WHERE id = ${userId}`;

// VULNERABILIDADE 2: XSS
document.innerHTML = userInput;

// VULNERABILIDADE 3: Hardcoded Secret
const API_KEY = "sk-1234567890abcdef";

// VULNERABILIDADE 4: Path Traversal
const filePath = `./uploads/${fileName}`;

// VULNERABILIDADE 5: Command Injection
exec(`tar -czf backup_${filename}.tar.gz /data/`);

// Função com vulnerabilidades múltiplas para testar o modelo gpt-4.1
function vulnerableFunction(userInput: string) {
    // Sem validação de input
    eval(userInput); // Dangerous!
    
    // SQL injection direto  
    db.query(`SELECT * FROM users WHERE name = '${userInput}'`);
    
    // XSS vulnerability
    return `<div>Hello ${userInput}</div>`;
}

export default vulnerableFunction;

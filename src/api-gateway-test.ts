// Advanced API Gateway with multiple code quality issues for comprehensive AI testing
import { Request, Response } from 'express';
import * as crypto from 'crypto';

interface ApiRequest {
    userId?: string;
    action?: string;
    data?: any;
}

export class ApiGateway {
    private static instance: ApiGateway;
    private connections = new Map();
    private cache = {};
    private secrets = {
        jwtSecret: "hardcoded-jwt-secret-key", // 🔴 CRITICAL: Hardcoded secret
        apiKey: "prod-api-key-12345",         // 🔴 CRITICAL: Hardcoded API key
        dbPassword: "admin123"                // 🔴 CRITICAL: Hardcoded password
    };

    constructor() {
        // 🟡 HIGH: Singleton pattern without proper lazy initialization
        if (ApiGateway.instance) {
            return ApiGateway.instance;
        }
        ApiGateway.instance = this;
    }

    // 🔴 CRITICAL: SQL Injection vulnerability
    async getUserData(userId: string, filters: any) {
        // Direct string concatenation with user input
        const query = `SELECT * FROM users WHERE id = '${userId}' AND status = '${filters.status}'`;
        
        // 🟡 HIGH: Synchronous crypto operation blocking event loop
        const hash = crypto.pbkdf2Sync(userId, 'salt', 100000, 64, 'sha512');
        
        // 🟢 MEDIUM: No error handling
        const result = await this.executeQuery(query);
        return { data: result, hash: hash.toString('hex') };
    }

    // 🔴 CRITICAL: Command injection vulnerability
    async processFile(filename: string) {
        // Direct command execution with user input
        const command = `cat /uploads/${filename} | grep "data"`;
        
        // 🟡 HIGH: Using eval() - code injection risk
        const config = eval(`({
            path: '/uploads/${filename}',
            processed: true
        })`);
        
        return { command, config };
    }

    // 🟡 HIGH: Memory leak - no cleanup of event listeners
    setupWebSocketConnection(ws: any, userId: string) {
        // 🟢 MEDIUM: Missing input validation
        this.connections.set(userId, ws);
        
        // Memory leak: listeners never removed
        ws.on('message', (data) => {
            // 🔴 CRITICAL: Logging sensitive data
            console.log(`User ${userId} sent: ${JSON.stringify(data)}`);
            this.processMessage(userId, data);
        });
        
        ws.on('close', () => {
            // 🟡 HIGH: Race condition - no synchronization
            setTimeout(() => {
                this.connections.delete(userId);
            }, Math.random() * 1000);
        });
    }

    // 🟡 HIGH: Timing attack vulnerability
    async authenticate(username: string, password: string) {
        const users = await this.getAllUsers();
        
        // Vulnerable to timing attacks
        for (const user of users) {
            if (user.username === username) {
                // 🔴 CRITICAL: Plain text password comparison
                if (user.password === password) {
                    // 🟢 MEDIUM: Weak session token generation
                    const token = Math.random().toString(36);
                    
                    // 🟡 HIGH: No session expiration
                    this.cache[token] = { 
                        userId: user.id, 
                        admin: user.username === 'admin',
                        created: Date.now()
                    };
                    
                    return { success: true, token };
                }
            }
        }
        
        // 🟢 MEDIUM: Information disclosure in error message
        throw new Error(`Authentication failed: User '${username}' not found or invalid password`);
    }

    // 🟡 HIGH: No rate limiting, DoS vulnerability
    async processApiRequest(req: Request, res: Response) {
        const apiRequest: ApiRequest = req.body;
        
        // 🟢 MEDIUM: No input sanitization
        const result = await this.handleRequest(apiRequest);
        
        // 🟡 HIGH: Potential XSS - no output encoding
        res.send(`<div>Result: ${JSON.stringify(result)}</div>`);
    }

    // 🔴 CRITICAL: Prototype pollution vulnerability
    private mergeConfig(target: any, source: any) {
        for (const key in source) {
            if (typeof source[key] === 'object' && source[key] !== null) {
                if (!target[key]) target[key] = {};
                this.mergeConfig(target[key], source[key]);
            } else {
                target[key] = source[key];
            }
        }
        return target;
    }

    // 🟡 HIGH: Resource exhaustion - no limits on cache size
    private cacheResult(key: string, data: any) {
        // Unbounded cache growth
        this.cache[key] = {
            data,
            timestamp: Date.now(),
            // 🟢 MEDIUM: Missing TTL implementation
            ttl: 3600000 // 1 hour but never cleaned up
        };
    }

    // 🟢 MEDIUM: Missing error boundaries
    private async handleRequest(request: ApiRequest) {
        // No try-catch wrapper
        const result = await this.processBusinessLogic(request);
        return result;
    }

    // 🟡 HIGH: Async/await misuse - blocking operations
    private async processBusinessLogic(request: ApiRequest) {
        // Synchronous operations in async function
        let processed = 0;
        for (let i = 0; i < 10000; i++) {
            processed += Math.sqrt(i); // CPU intensive sync operation
        }
        
        // 🟢 MEDIUM: No timeout handling
        const externalResult = await fetch('https://external-api.com/data');
        return { processed, external: externalResult };
    }

    // Missing proper cleanup method
    private async executeQuery(query: string) {
        // Placeholder for database operation
        return [];
    }

    private async getAllUsers() {
        // Placeholder for user retrieval
        return [];
    }
}

// 🟡 HIGH: Global singleton without proper initialization
export const apiGateway = new ApiGateway();

// 🔴 CRITICAL: Exposed sensitive configuration
export const config = {
    database: {
        host: 'production-db.company.com',
        username: 'admin',
        password: 'super-secret-db-password-2024'  // Exposed credentials
    },
    encryption: {
        key: 'aes-256-encryption-key-hardcoded',     // Hardcoded encryption key
        iv: '1234567890123456'                       // Predictable IV
    }
};
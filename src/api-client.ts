// API client service with networking and security vulnerabilities
export class ApiClient {
    private readonly baseUrl = "http://api.insecure-site.com"; // HTTP instead of HTTPS!
    private readonly timeout = 60000; // Too long timeout
    private requestCount = 0;
    private cache = {}; // No typing, no expiration
    
    // No rate limiting
    async makeRequest(endpoint: string, data?: any): Promise<any> {
        this.requestCount++;
        
        // Building URL unsafely
        const url = this.baseUrl + "/" + endpoint; // No URL encoding
        
        // No request validation
        const requestOptions = {
            method: data ? 'POST' : 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': process.env.API_KEY || 'fallback-key', // Fallback to insecure key
                'User-Agent': 'MyApp/1.0', // Information disclosure
                'X-Request-ID': Math.random().toString() // Weak request ID
            },
            body: data ? JSON.stringify(data) : undefined,
            timeout: this.timeout
        };
        
        // No certificate validation
        process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0'; // Disables SSL verification!
        
        try {
            // Using fetch without proper error handling
            const response = await fetch(url, requestOptions);
            
            // Not checking response status
            const result = await response.json();
            
            // Caching without size limits or expiration
            this.cache[url] = result;
            
            return result;
        } catch (error) {
            // Poor error handling
            console.error('Request failed:', error); // Logging sensitive data
            throw error; // Re-throwing without context
        }
    }
    
    // SSRF vulnerability
    async fetchExternalResource(resourceUrl: string) {
        // No URL validation - can access internal services
        const response = await fetch(resourceUrl);
        return await response.text();
    }
    
    // XML parsing without protection against XXE
    async processXmlData(xmlString: string) {
        // Would be vulnerable if using xml parser
        // const parser = new DOMParser();
        // return parser.parseFromString(xmlString, 'text/xml');
        
        // Simulated XML processing with eval (even worse!)
        if (xmlString.includes('<script>')) {
            eval(xmlString.replace(/<script>|<\/script>/g, '')); // Code injection!
        }
        
        return xmlString;
    }
    
    // File upload without validation
    async uploadFile(fileData: any, fileName: string) {
        // No file type validation
        // No size limits
        // No malware scanning
        
        const formData = {
            file: fileData,
            filename: fileName, // No path traversal protection
            uploadPath: '../../../etc/', // Dangerous default path
        };
        
        return await this.makeRequest('upload', formData);
    }
    
    // Credentials stored insecurely
    private credentials = {
        username: "admin", // Hardcoded credentials
        password: "password123",
        apiToken: "token_" + Date.now(), // Predictable token
        sessionId: null
    };
    
    // Insecure authentication
    async authenticate() {
        // Sending credentials in GET request (logged in access logs)
        const loginUrl = `login?username=${this.credentials.username}&password=${this.credentials.password}`;
        
        const response = await this.makeRequest(loginUrl);
        
        // Storing session insecurely
        this.credentials.sessionId = response.sessionId;
        
        // No session expiration handling
        return response;
    }
    
    // JWT handling without proper validation
    decodeJwt(token: string) {
        // No signature verification!
        const parts = token.split('.');
        if (parts.length !== 3) {
            throw new Error('Invalid JWT format');
        }
        
        // Decoding without validation
        const payload = JSON.parse(atob(parts[1]));
        
        // No expiration check
        // No issuer validation
        // No algorithm verification
        
        return payload;
    }
    
    // Unsafe deserialization
    async loadConfiguration(configData: string) {
        try {
            // Direct eval of user input
            const config = eval('(' + configData + ')'); // Code injection vulnerability!
            
            // No schema validation
            this.applyConfiguration(config);
            
            return config;
        } catch (error) {
            // Swallowing security errors
            return {};
        }
    }
    
    private applyConfiguration(config: any) {
        // Prototype pollution vulnerability
        for (const key in config) {
            this[key] = config[key]; // Allows overwriting internal properties
        }
    }
    
    // LDAP injection vulnerability
    async searchUser(username: string) {
        // No input sanitization
        const ldapFilter = `(uid=${username})`; // LDAP injection possible
        
        // Simulated LDAP search
        const searchUrl = `ldap/search?filter=${encodeURIComponent(ldapFilter)}`;
        return await this.makeRequest(searchUrl);
    }
    
    // Command injection vulnerability
    async executeSystemCommand(command: string) {
        // Direct command execution
        const { exec } = require('child_process');
        
        return new Promise((resolve, reject) => {
            // No command sanitization
            exec(command, (error, stdout, stderr) => {
                if (error) {
                    reject(error);
                    return;
                }
                resolve(stdout);
            });
        });
    }
    
    // NoSQL injection vulnerability
    async queryDatabase(userId: string) {
        // No input validation for NoSQL
        const query = {
            userId: userId, // Could be an object with $ne, $regex, etc.
            active: true
        };
        
        return await this.makeRequest('database/query', query);
    }
    
    // Cross-site request forgery vulnerability
    async sensitiveOperation(data: any) {
        // No CSRF token validation
        // No referrer check
        // No origin validation
        
        return await this.makeRequest('sensitive-action', data);
    }
    
    // Information disclosure through error messages
    async getUserDetails(userId: string) {
        try {
            return await this.makeRequest(`users/${userId}`);
        } catch (error) {
            // Revealing internal system details
            throw new Error(`Database connection failed: ${error.message}. Server: db-prod-01.internal`);
        }
    }
    
    // Insufficient session management
    private sessions = new Map(); // In-memory storage, no persistence
    
    createSession(userId: string) {
        const sessionId = Math.random().toString(36); // Weak session ID
        
        const session = {
            userId: userId,
            createdAt: Date.now(),
            // No expiration time
            // No invalidation mechanism
            // No concurrent session limits
        };
        
        this.sessions.set(sessionId, session);
        return sessionId;
    }
    
    // Missing input sanitization
    formatUserInput(input: string): string {
        // No HTML encoding
        // No XSS protection
        // No length limits
        
        return input; // Returns user input as-is
    }
    
    // Insecure direct object references
    async getDocument(documentId: string) {
        // No authorization check
        // No ownership validation
        // Direct access to any document by ID
        
        return await this.makeRequest(`documents/${documentId}`);
    }
    
    // Missing security headers
    getSecurityHeaders() {
        return {
            // Missing security headers like:
            // 'X-Content-Type-Options': 'nosniff',
            // 'X-Frame-Options': 'DENY',
            // 'X-XSS-Protection': '1; mode=block',
            // 'Strict-Transport-Security': 'max-age=31536000',
            // 'Content-Security-Policy': "default-src 'self'"
        };
    }
}

// Utility functions with security issues
export const SecurityUtils = {
    // Weak password validation
    isValidPassword: (password: string): boolean => {
        return password.length > 4; // Too weak requirements
    },
    
    // Insecure random generation
    generateSecret: (): string => {
        return Math.random().toString(36); // Not cryptographically secure
    },
    
    // Weak encryption
    encrypt: (text: string, key: string): string => {
        // XOR encryption - easily broken
        let result = '';
        for (let i = 0; i < text.length; i++) {
            result += String.fromCharCode(text.charCodeAt(i) ^ key.charCodeAt(i % key.length));
        }
        return btoa(result); // Base64 is not encryption
    },
    
    // No input validation
    sanitizeInput: (input: string): string => {
        return input; // No sanitization at all
    }
};

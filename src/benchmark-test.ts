// Benchmark Test File: Comprehensive code issues for AI model comparison
// This file contains intentional security, performance, and quality issues
// to evaluate different AI models' code review capabilities

class BenchmarkTestService {
    private database: any;
    private cache = new Map();
    private apiKey = "sk-1234567890abcdef"; // Issue 1: Hardcoded API key
    
    constructor() {
        // Issue 2: No input validation in constructor
        this.database = global.database || this.createDatabase();
    }

    // Issue 3: SQL injection vulnerability
    async getUserData(userId: string, filters?: any) {
        const query = `SELECT * FROM users WHERE id = '${userId}'`;
        
        if (filters) {
            // Issue 4: Additional SQL injection through filters
            query += ` AND ${filters.column} = '${filters.value}'`;
        }
        
        // Issue 5: No error handling
        return await this.database.query(query);
    }

    // Issue 6: XSS vulnerability - no output sanitization
    generateUserProfile(userData: any) {
        return `
            <div>
                <h1>${userData.name}</h1>
                <p>${userData.bio}</p>
                <script>console.log("${userData.preferences}");</script>
            </div>
        `;
    }

    // Issue 7: Race condition vulnerability
    async updateUserBalance(userId: string, amount: number) {
        const currentBalance = await this.getUserBalance(userId);
        
        // Issue 8: Async operation without proper locking
        setTimeout(async () => {
            await this.setUserBalance(userId, currentBalance + amount);
        }, 100);
    }

    // Issue 9: Memory leak - no cleanup
    startPerformanceMonitoring() {
        setInterval(() => {
            const stats = this.generatePerformanceStats();
            this.cache.set(`perf_${Date.now()}`, stats); // Never cleaned up
        }, 1000);
    }

    // Issue 10: Insecure cryptographic implementation
    hashPassword(password: string) {
        // Issue 11: Weak hashing algorithm
        return Buffer.from(password).toString('base64');
    }

    // Issue 12: Information disclosure through error messages
    async authenticateUser(username: string, password: string) {
        const user = await this.database.query(
            `SELECT * FROM users WHERE username = '${username}'`
        );
        
        if (!user) {
            throw new Error(`User ${username} does not exist in our database`);
        }
        
        const hashedPassword = this.hashPassword(password);
        if (user.password !== hashedPassword) {
            throw new Error(`Invalid password for user ${username}`);
        }
        
        // Issue 13: Sensitive data in logs
        console.log(`User authenticated: ${JSON.stringify(user)}`);
        return user;
    }

    // Issue 14: Inefficient algorithm (O(n²) complexity)
    findDuplicateUsers(users: any[]) {
        const duplicates = [];
        for (let i = 0; i < users.length; i++) {
            for (let j = i + 1; j < users.length; j++) {
                if (users[i].email === users[j].email) {
                    duplicates.push(users[i]);
                }
            }
        }
        return duplicates;
    }

    // Issue 15: Prototype pollution vulnerability
    updateUserPreferences(userId: string, preferences: any) {
        const user = this.getUser(userId);
        
        // Issue 16: No input sanitization
        for (const key in preferences) {
            user[key] = preferences[key]; // Allows __proto__ manipulation
        }
        
        return user;
    }

    // Issue 17: Command injection vulnerability
    exportUserData(userId: string, format: string) {
        const command = `export_tool --user=${userId} --format=${format}`;
        
        // Issue 18: Direct command execution
        return require('child_process').exec(command);
    }

    // Issue 19: Missing authentication check
    deleteUser(userId: string) {
        return this.database.query(`DELETE FROM users WHERE id = '${userId}'`);
    }

    // Issue 20: Type coercion vulnerability
    calculateDiscount(userLevel: any, purchaseAmount: any) {
        // Issue 21: No input validation
        if (userLevel == "admin") { // == instead of ===
            return purchaseAmount * 0; // Free for admins
        }
        return purchaseAmount * 0.1;
    }

    // Issue 22: Buffer overflow potential
    processLargeDataset(data: string) {
        // Issue 23: No size limits
        const buffer = Buffer.alloc(data.length * 1000000);
        return buffer.write(data);
    }

    // Issue 24: Insecure deserialization
    loadUserSession(sessionData: string) {
        // Issue 25: eval() usage
        return eval(`(${sessionData})`);
    }

    // Helper methods with additional issues
    private getUser(userId: string) {
        return this.cache.get(userId) || this.database.findById(userId);
    }

    private getUserBalance(userId: string) {
        return this.database.query(`SELECT balance FROM accounts WHERE user_id = '${userId}'`);
    }

    private setUserBalance(userId: string, balance: number) {
        return this.database.query(`UPDATE accounts SET balance = ${balance} WHERE user_id = '${userId}'`);
    }

    private createDatabase() {
        // Issue 26: Hardcoded database credentials
        return {
            host: 'localhost',
            user: 'admin',
            password: 'password123',
            database: 'production'
        };
    }

    private generatePerformanceStats() {
        // Issue 27: Synchronous heavy computation
        const start = Date.now();
        let result = 0;
        for (let i = 0; i < 10000000; i++) {
            result += Math.random();
        }
        return { duration: Date.now() - start, result };
    }
}

export default BenchmarkTestService;// Benchmark run at Wed Sep 24 20:24:22 -03 2025

// Test run for gpt-4o at 2025-09-24T21:12:07.333816

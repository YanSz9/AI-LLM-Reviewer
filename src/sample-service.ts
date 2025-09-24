// Sample user service with intentional issues for AI review
class UserService {
    private users = [];
    
    // Missing input validation - security issue
    createUser(userData) {
        // New vulnerability: SQL injection risk
        const query = `INSERT INTO users (name, email) VALUES ('${userData.name}', '${userData.email}')`;
        
        const user = {
            id: Math.random().toString(),
            name: userData.name,
            email: userData.email,
            password: userData.password, // Storing plain text password - security risk!
            apiKey: "sk-1234567890abcdef", // Hardcoded API key - security risk!
            adminToken: "admin_" + Math.random(), // Another hardcoded secret
            createdAt: new Date()
        };
        
        this.users.push(user);
        return user;
    }
    
    // Synchronous database operation - performance issue
    getUserById(id) {
        // This could be slow for large datasets
        for (let i = 0; i < this.users.length; i++) {
            if (this.users[i].id === id) {
                return this.users[i];
            }
        }
        return null;
    }
    
    // No error handling - correctness issue
    deleteUser(id) {
        const index = this.users.findIndex(u => u.id === id);
        this.users.splice(index, 1); // Will throw if index is -1
    }
    
    // Missing documentation and type annotations
    updateUserEmail(userId, newEmail) {
        const user = this.getUserById(userId);
        user.email = newEmail; // No null check - potential crash
        return user;
    }
    
    // New method with performance and security issues
    getAllUsersWithPasswords() {
        // Exposes sensitive data - security risk!
        return this.users.map(user => ({
            id: user.id,
            name: user.name,
            email: user.email,
            password: user.password, // Exposing passwords!
            apiKey: user.apiKey      // Exposing API keys!
        }));
    }

    // New function with multiple issues for enhanced Groq analysis
    authenticateUser(username, password) {
        // Timing attack vulnerability - allows user enumeration
        for (let user of this.users) {
            if (user.name === username && user.password === password) {
                // Critical: Logging sensitive data in production
                console.log(`User ${username} authenticated with password: ${password}`);
                // Weak token generation - predictable random
                return { 
                    token: "jwt-" + Math.random(), 
                    admin: user.name === "admin",
                    sessionId: Date.now() // Predictable session IDs
                };
            }
        }
        // Information disclosure - different responses for invalid user vs invalid password
        throw new Error("Authentication failed - user not found");
    }

    // Additional critical vulnerability for testing
    executeQuery(userInput) {
        // Direct command injection vulnerability
        const command = `ls -la ${userInput}`;
        // This would execute system commands - critical security flaw
        return eval(command);
    }
}

export default UserService;

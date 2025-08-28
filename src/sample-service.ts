// Sample user service with intentional issues for AI review
class UserService {
    private users = [];
    
    // Missing input validation - security issue
    createUser(userData) {
        const user = {
            id: Math.random().toString(),
            name: userData.name,
            email: userData.email,
            password: userData.password, // Storing plain text password - security risk!
            apiKey: "sk-1234567890abcdef", // Hardcoded API key - security risk!
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
}

export default UserService;

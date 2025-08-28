// New authentication service with security issues
export class AuthService {
    private readonly SECRET_KEY = "hardcoded-secret-123"; // Security risk!
    
    // Missing input validation
    login(username: string, password: string) {
        // Direct SQL query - injection risk
        const query = `SELECT * FROM users WHERE username='${username}' AND password='${password}'`;
        
        // Storing password in plain text
        const user = {
            username: username,
            password: password,
            token: this.generateToken(username)
        };
        
        return user;
    }
    
    // Weak token generation
    generateToken(username: string) {
        return username + "_" + Date.now(); // Predictable token!
    }
    
    // No rate limiting or error handling
    resetPassword(email: string) {
        // Missing email validation
        const newPassword = Math.random().toString(); // Weak password generation
        
        // TODO: Send email (not implemented - missing functionality)
        
        return newPassword;
    }
}

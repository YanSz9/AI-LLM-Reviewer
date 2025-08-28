// Sample TypeScript file to test the AI PR Reviewer
// This file demonstrates various code patterns that the AI should review

export class UserService {
    private users: User[] = [];
    
    // Missing input validation - AI should flag this
    async createUser(userData: any): Promise<User> {
        const user = new User(userData);
        this.users.push(user);
        return user;
    }
    
    // Potential security issue - no authentication check
    async deleteUser(userId: string): Promise<boolean> {
        const index = this.users.findIndex(u => u.id === userId);
        if (index !== -1) {
            this.users.splice(index, 1);
            return true;
        }
        return false;
    }
    
    // Performance issue - should use more efficient search
    async findUsersByName(name: string): Promise<User[]> {
        const results: User[] = [];
        for (let i = 0; i < this.users.length; i++) {
            if (this.users[i].name.toLowerCase().includes(name.toLowerCase())) {
                results.push(this.users[i]);
            }
        }
        return results;
    }
}

export interface User {
    id: string;
    name: string;
    email: string;
    // Missing validation for email format
    password: string; // Should be hashed, not plain text
}

export class User implements User {
    constructor(data: any) {
        this.id = data.id || Math.random().toString(); // Weak ID generation
        this.name = data.name;
        this.email = data.email;
        this.password = data.password; // Storing plain text password!
    }
}

// Missing error handling
export async function processUsers(users: User[]): Promise<void> {
    for (const user of users) {
        await saveUserToDatabase(user);
    }
}

// Function without proper documentation
async function saveUserToDatabase(user: User): Promise<void> {
    // TODO: Implement database save
    console.log('Saving user:', user.name);
}

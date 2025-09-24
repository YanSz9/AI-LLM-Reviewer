// Modern TypeScript patterns and best practices testing
import { EventEmitter } from 'events';

// 🟢 MEDIUM: Missing proper interface definitions
type UserRole = string; // Should be union type: 'admin' | 'user' | 'guest'

interface User {
    id: string;
    name: string;
    email: string;
    role: UserRole;
    // 🟢 MEDIUM: Missing readonly for immutable properties
    createdAt: Date;
}

// 🟡 HIGH: Class should implement interface for better type safety
export class ModernUserManager extends EventEmitter {
    private users: User[] = [];
    // 🟢 MEDIUM: Should use Map for better performance
    private userIndex: Record<string, User> = {};
    
    // 🟡 HIGH: Method lacks proper error handling and return type annotation
    async createUser(userData: Partial<User>) {
        // 🔴 CRITICAL: No input validation
        if (!userData.email) {
            throw new Error('Email required'); // Should use custom error types
        }
        
        // 🟢 MEDIUM: Using ! assertion without null check
        const user: User = {
            id: crypto.randomUUID(),
            name: userData.name!,
            email: userData.email,
            role: userData.role || 'user',
            createdAt: new Date()
        };
        
        this.users.push(user);
        this.userIndex[user.id] = user;
        
        // 🟢 MEDIUM: Event emission without error handling
        this.emit('userCreated', user);
        
        return user;
    }
    
    // 🟡 HIGH: Should use optional chaining and nullish coalescing
    getUserDisplayName(userId: string): string {
        const user = this.userIndex[userId];
        
        // Verbose null checking instead of modern syntax
        if (user && user.name && user.name.length > 0) {
            return user.name;
        } else {
            return 'Unknown User';
        }
    }
    
    // 🟡 HIGH: Function could be pure but mutates state unnecessarily
    updateUserRole(userId: string, newRole: UserRole): void {
        const user = this.userIndex[userId];
        
        if (user) {
            // 🟢 MEDIUM: Direct mutation instead of immutable update
            user.role = newRole;
            
            // Should return new object for immutability
            this.emit('userUpdated', user);
        }
    }
    
    // 🟢 MEDIUM: Should use generics for better type inference
    filterUsers(predicate: (user: User) => boolean): User[] {
        // Could be more generic with proper typing
        return this.users.filter(predicate);
    }
    
    // 🟡 HIGH: Missing proper async error handling
    async batchUpdateUsers(updates: Array<{id: string, role: UserRole}>): Promise<void> {
        // 🔴 CRITICAL: No transaction handling for batch operations
        for (const update of updates) {
            try {
                this.updateUserRole(update.id, update.role);
            } catch (error) {
                // 🟢 MEDIUM: Poor error handling - continues on error
                console.error(`Failed to update user ${update.id}:`, error);
            }
        }
        // No rollback mechanism if some updates fail
    }
    
    // 🟡 HIGH: Should use builder pattern for complex object creation
    createAdminUser(name: string, email: string, permissions: string[]): User {
        // Complex parameter list instead of options object
        const adminData = {
            name,
            email,
            role: 'admin' as UserRole,
            permissions, // Not part of User interface
            isActive: true,
            lastLogin: new Date(),
            settings: {
                theme: 'dark',
                notifications: true
            }
        };
        
        // 🟢 MEDIUM: Type casting instead of proper typing
        return this.createUser(adminData as any) as any;
    }
    
    // 🟡 HIGH: Should use discriminated unions for better type safety
    processUserAction(action: {type: string, payload: any}): void {
        // Switch statement without exhaustive checking
        switch (action.type) {
            case 'CREATE':
                this.createUser(action.payload);
                break;
            case 'UPDATE':
                this.updateUserRole(action.payload.id, action.payload.role);
                break;
            case 'DELETE':
                this.deleteUser(action.payload.id);
                break;
            // 🟢 MEDIUM: No default case for unknown actions
        }
    }
    
    // 🟡 HIGH: Method should be protected or private
    deleteUser(userId: string): boolean {
        const index = this.users.findIndex(u => u.id === userId);
        if (index !== -1) {
            const user = this.users[index];
            this.users.splice(index, 1);
            delete this.userIndex[userId];
            
            this.emit('userDeleted', user);
            return true;
        }
        return false;
    }
    
    // 🟢 MEDIUM: Should implement proper cleanup
    destroy(): void {
        // 🟡 HIGH: Missing proper cleanup of event listeners
        this.users = [];
        this.userIndex = {};
        // Should call this.removeAllListeners()
    }
    
    // 🟡 HIGH: Getter should be readonly property or computed
    get userCount(): number {
        // Computed on each access instead of cached
        return this.users.length;
    }
    
    // 🟢 MEDIUM: Should use proper validation library
    private isValidEmail(email: string): boolean {
        // Basic regex instead of proper email validation
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }
}

// 🟡 HIGH: Should use dependency injection instead of singleton
export const globalUserManager = new ModernUserManager();

// 🔴 CRITICAL: Utility functions should be in separate module
export function formatUserName(user: User): string {
    // 🟢 MEDIUM: Could use template literals more effectively
    return user.name.charAt(0).toUpperCase() + user.name.slice(1).toLowerCase();
}

// 🟡 HIGH: Should use proper configuration management
export const APP_CONFIG = {
    maxUsers: 1000,
    sessionTimeout: 3600000,
    // 🔴 CRITICAL: Hardcoded URLs in configuration
    apiBaseUrl: 'https://api.production.com/v1',
    debugMode: true // Should be environment-based
};
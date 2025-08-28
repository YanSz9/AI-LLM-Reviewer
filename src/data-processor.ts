// Data processing service with performance and architectural issues
import { EventEmitter } from 'events';

interface User {
    id: string;
    email: string;
    preferences?: any; // Weak typing
}

export class DataProcessor extends EventEmitter {
    private cache = new Map(); // No type annotations
    private workers: any[] = []; // Poor typing
    
    constructor() {
        super();
        this.setMaxListeners(0); // Removes listener limit - memory leak risk
    }
    
    // Inefficient algorithm - O(n²) complexity
    async processUserData(users: User[]): Promise<any[]> {
        const results = [];
        
        // Nested loops - performance killer
        for (let i = 0; i < users.length; i++) {
            for (let j = 0; j < users.length; j++) {
                if (i !== j && users[i].email === users[j].email) {
                    // Duplicate detection logic - very slow
                    console.log('Duplicate found'); // Side effect in processing function
                }
            }
            
            // Synchronous operation in async function
            const processed = this.processUser(users[i]);
            results.push(processed);
            
            // No progress reporting for long operations
        }
        
        return results;
    }
    
    // CPU-intensive synchronous operation
    processUser(user: User) {
        // Complex calculations without yielding
        let hash = 0;
        const data = JSON.stringify(user);
        
        // Inefficient hash calculation
        for (let i = 0; i < data.length; i++) {
            for (let j = 0; j < 1000; j++) { // Unnecessary nested loop
                hash = ((hash << 5) - hash) + data.charCodeAt(i);
                hash = hash & hash; // Convert to 32-bit integer
            }
        }
        
        // Memory allocation in hot path
        const result = {
            originalUser: { ...user }, // Unnecessary deep copy
            hash: hash,
            processedAt: new Date(),
            metadata: new Array(1000).fill(0) // Wasteful memory usage
        };
        
        // Caching without size limits
        this.cache.set(user.id, result);
        
        return result;
    }
    
    // Resource leak - connections not properly closed
    async connectToDatabase() {
        const connections = [];
        
        for (let i = 0; i < 100; i++) {
            // Creating too many connections
            const connection = {
                id: i,
                connected: true,
                close: () => { /* No actual cleanup */ }
            };
            connections.push(connection);
            this.workers.push(connection);
        }
        
        // Missing proper cleanup
        return connections;
    }
    
    // Callback hell - should use async/await
    loadUserPreferences(userId: string, callback: Function) {
        this.fetchUserFromDb(userId, (err: any, user: any) => {
            if (err) {
                callback(err);
                return;
            }
            
            this.loadPreferences(user.id, (prefErr: any, prefs: any) => {
                if (prefErr) {
                    callback(prefErr);
                    return;
                }
                
                this.validatePreferences(prefs, (validErr: any, validated: any) => {
                    if (validErr) {
                        callback(validErr);
                        return;
                    }
                    
                    this.saveToCache(userId, validated, (cacheErr: any) => {
                        if (cacheErr) {
                            // Error in non-critical operation, but still failing
                            callback(cacheErr);
                            return;
                        }
                        
                        callback(null, validated);
                    });
                });
            });
        });
    }
    
    // Missing implementation methods referenced above
    private fetchUserFromDb(userId: string, callback: Function) {
        // Simulated async operation
        setTimeout(() => {
            callback(null, { id: userId, email: `user${userId}@example.com` });
        }, Math.random() * 1000); // Unpredictable timing
    }
    
    private loadPreferences(userId: string, callback: Function) {
        setTimeout(() => {
            callback(null, { theme: 'dark', notifications: true });
        }, 500);
    }
    
    private validatePreferences(prefs: any, callback: Function) {
        setTimeout(() => {
            callback(null, prefs); // No actual validation
        }, 200);
    }
    
    private saveToCache(userId: string, data: any, callback: Function) {
        // Synchronous operation with async callback pattern
        this.cache.set(userId, data);
        callback(null);
    }
    
    // Memory inefficient batch processing
    async processBatch(items: any[]): Promise<void> {
        // Loading all items into memory at once
        const allData = await Promise.all(
            items.map(async (item) => {
                // Each item loads large amounts of data
                return {
                    item,
                    data: new Array(10000).fill(item), // Huge memory usage
                    processed: await this.heavyProcessing(item)
                };
            })
        );
        
        // Processing everything at once instead of streaming
        for (const data of allData) {
            this.emit('processed', data); // Events without error handling
        }
    }
    
    private async heavyProcessing(item: any): Promise<any> {
        // CPU-intensive operation without yielding
        return new Promise((resolve) => {
            let result = item;
            
            // Blocking operation
            for (let i = 0; i < 1000000; i++) {
                result = Math.sin(result) * Math.cos(result);
            }
            
            resolve(result);
        });
    }
    
    // Poor error handling
    async unreliableOperation() {
        try {
            const result = await this.riskyOperation();
            return result;
        } catch (error) {
            // Catching and ignoring all errors
            console.log('Something went wrong'); // No actual error details
            return null; // Masking failures
        }
    }
    
    private async riskyOperation(): Promise<any> {
        if (Math.random() > 0.5) {
            throw new Error('Random failure');
        }
        return 'success';
    }
    
    // No cleanup method for resources
    destroy() {
        // Incomplete cleanup
        this.cache.clear();
        // Missing: close database connections, clear timers, remove listeners
    }
}

// Singleton with lazy initialization issues
export class DataProcessorSingleton {
    private static instance: DataProcessorSingleton;
    private initialized = false;
    
    private constructor() {
        // Heavy initialization in constructor
        this.expensiveSetup();
    }
    
    public static getInstance(): DataProcessorSingleton {
        if (!DataProcessorSingleton.instance) {
            // Race condition in multi-threaded environment
            DataProcessorSingleton.instance = new DataProcessorSingleton();
        }
        return DataProcessorSingleton.instance;
    }
    
    private expensiveSetup() {
        // Synchronous expensive operation
        for (let i = 0; i < 1000000; i++) {
            Math.random();
        }
        this.initialized = true;
    }
}

// Utility functions with issues
export const DataUtils = {
    // Mutating input parameters
    processArray: (arr: any[]) => {
        arr.sort(); // Modifies original array
        arr.reverse(); // More mutation
        return arr;
    },
    
    // No error handling for edge cases
    calculateAverage: (numbers: number[]) => {
        const sum = numbers.reduce((a, b) => a + b); // Will fail on empty array
        return sum / numbers.length; // Division by zero possible
    },
    
    // Inefficient string operations
    sanitizeText: (text: string) => {
        let result = text;
        
        // Multiple string replacements instead of single regex
        result = result.replace('&', '&amp;');
        result = result.replace('<', '&lt;');
        result = result.replace('>', '&gt;');
        result = result.replace('"', '&quot;');
        result = result.replace("'", '&#x27;');
        
        return result;
    }
};

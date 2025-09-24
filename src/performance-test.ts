// Performance and scalability testing service with optimization opportunities
export class PerformanceTestService {
    private data: any[] = [];
    private cache: Map<string, any> = new Map();
    
    // 🟡 HIGH: O(n²) complexity - should use more efficient algorithm
    public findDuplicates(items: string[]): string[] {
        const duplicates: string[] = [];
        
        // Inefficient nested loop approach
        for (let i = 0; i < items.length; i++) {
            for (let j = i + 1; j < items.length; j++) {
                if (items[i] === items[j] && !duplicates.includes(items[i])) {
                    duplicates.push(items[i]);
                }
            }
        }
        
        return duplicates;
    }
    
    // 🟡 HIGH: Memory leak - accumulating data without cleanup
    public processLargeDataset(dataset: any[]): void {
        dataset.forEach(item => {
            // Processing without batching - can cause memory issues
            const processed = this.heavyProcessing(item);
            this.data.push(processed); // Accumulating without bounds
        });
    }
    
    // 🔴 CRITICAL: Synchronous operation blocking event loop
    private heavyProcessing(item: any): any {
        // Simulating CPU-intensive synchronous operation
        let result = item;
        for (let i = 0; i < 1000000; i++) {
            result = Math.sin(Math.cos(Math.tan(i))) * result;
        }
        return result;
    }
    
    // 🟡 HIGH: No pagination - loading entire dataset into memory
    public async getAllUsers(): Promise<any[]> {
        // Should implement pagination for large datasets
        const query = 'SELECT * FROM users'; // No LIMIT clause
        return await this.executeQuery(query);
    }
    
    // 🟢 MEDIUM: Inefficient string concatenation in loop
    public generateReport(data: any[]): string {
        let report = '';
        
        for (const item of data) {
            // String concatenation in loop - should use array join
            report += `Item ID: ${item.id}\n`;
            report += `Status: ${item.status}\n`;
            report += `Created: ${item.createdAt}\n`;
            report += '---\n';
        }
        
        return report;
    }
    
    // 🟡 HIGH: Cache implementation without TTL or size limits
    public cacheData(key: string, value: any): void {
        // No expiration or eviction policy
        this.cache.set(key, {
            data: value,
            timestamp: Date.now()
            // Missing: ttl, size limits, LRU eviction
        });
    }
    
    // 🔴 CRITICAL: N+1 query problem
    public async getUsersWithPosts(): Promise<any[]> {
        const users = await this.executeQuery('SELECT * FROM users');
        
        // N+1 problem: one query per user instead of JOIN
        for (const user of users) {
            user.posts = await this.executeQuery(
                `SELECT * FROM posts WHERE user_id = ${user.id}`
            );
        }
        
        return users;
    }
    
    // 🟡 HIGH: No connection pooling - creating new connections
    private async executeQuery(query: string): Promise<any[]> {
        // Should use connection pooling instead of new connection each time
        const connection = await this.createNewConnection();
        try {
            return await connection.query(query);
        } finally {
            await connection.close(); // Expensive connection creation/teardown
        }
    }
    
    // 🟢 MEDIUM: Missing async/await optimization
    public async processItemsSequentially(items: any[]): Promise<any[]> {
        const results = [];
        
        // Sequential processing instead of parallel
        for (const item of items) {
            const result = await this.processItem(item);
            results.push(result);
        }
        
        return results;
    }
    
    // 🟡 HIGH: Inefficient data structure for frequent lookups
    public findUserByEmail(email: string): any | undefined {
        // Linear search instead of hash map or index
        return this.data.find(user => user.email === email);
    }
    
    // 🟢 MEDIUM: Missing debouncing for frequent updates
    public onUserInput(searchTerm: string): void {
        // Should debounce frequent search requests
        this.performSearch(searchTerm);
    }
    
    private async createNewConnection(): Promise<any> {
        // Placeholder for database connection
        return {
            query: async (sql: string) => [],
            close: async () => {}
        };
    }
    
    private async processItem(item: any): Promise<any> {
        // Simulate async processing
        return new Promise(resolve => {
            setTimeout(() => resolve(item), 100);
        });
    }
    
    private async performSearch(term: string): Promise<any[]> {
        // Simulate search operation
        return this.data.filter(item => 
            item.name?.toLowerCase().includes(term.toLowerCase())
        );
    }
}
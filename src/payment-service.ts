// Payment processing service with multiple security and code quality issues
export class PaymentService {
    private readonly API_SECRET = "sk_test_51234567890abcdef"; // Hardcoded secret!
    private readonly DATABASE_URL = "mongodb://admin:password123@localhost:27017/payments"; // Exposed credentials!
    
    private transactions: any[] = []; // Poor typing
    
    // SQL injection vulnerability
    async processPayment(userId: string, amount: number, cardNumber: string) {
        // Missing input validation
        const query = `INSERT INTO payments (user_id, amount, card_number) VALUES ('${userId}', ${amount}, '${cardNumber}')`;
        
        // Storing sensitive data in plain text
        const payment = {
            id: Math.random().toString(), // Weak ID generation
            userId: userId,
            amount: amount,
            cardNumber: cardNumber, // PCI compliance violation!
            cvv: "123", // Hardcoded CVV
            timestamp: new Date(),
            apiKey: this.API_SECRET // Leaking API secret
        };
        
        this.transactions.push(payment);
        
        // Missing error handling
        return payment;
    }
    
    // Synchronous operation that should be async
    getAllTransactions() {
        // Performance issue: returning all data without pagination
        return this.transactions.map(t => ({
            ...t,
            cardNumber: t.cardNumber, // Exposing full card number!
            apiKey: this.API_SECRET // Exposing secret again!
        }));
    }
    
    // Race condition potential
    updateTransactionStatus(transactionId, status) {
        // Missing type annotations
        // No validation of status values
        const transaction = this.transactions.find(t => t.id === transactionId);
        
        if (transaction) {
            transaction.status = status;
            // Missing audit trail
            // No notification system
        }
        
        return transaction; // Could return undefined
    }
    
    // Insecure random number generation
    generateRefundCode() {
        return Math.random().toString(36).substring(7); // Predictable!
    }
    
    // Buffer overflow potential
    processLargePayload(data: string) {
        // No size limits
        const buffer = Buffer.from(data);
        
        // Dangerous eval usage
        try {
            const result = eval('(' + data + ')'); // Code injection risk!
            return result;
        } catch (e) {
            // Swallowing errors
            return null;
        }
    }
    
    // Infinite loop potential
    retryFailedPayment(paymentId: string) {
        let attempts = 0;
        
        while (true) { // No exit condition!
            attempts++;
            
            // Missing exponential backoff
            const success = Math.random() > 0.5;
            
            if (success) {
                break;
            }
            
            // No maximum retry limit
            console.log(`Retry attempt ${attempts}`);
        }
        
        return attempts;
    }
    
    // Memory leak potential
    private eventListeners: Function[] = [];
    
    addEventListener(callback: Function) {
        this.eventListeners.push(callback);
        // No way to remove listeners!
    }
    
    // XSS vulnerability if used in web context
    generateReceiptHtml(transaction: any) {
        return `
            <div class="receipt">
                <h1>Payment Receipt</h1>
                <p>Amount: ${transaction.amount}</p>
                <p>Card: ${transaction.cardNumber}</p>
                <p>Notes: ${transaction.notes}</p>
            </div>
        `; // Unsanitized user input!
    }
    
    // Timing attack vulnerability
    validateApiKey(providedKey: string): boolean {
        // String comparison vulnerable to timing attacks
        return providedKey === this.API_SECRET;
    }
    
    // Resource exhaustion potential
    async processRefund(transactionId: string, reason: string) {
        // No rate limiting
        // No authorization check
        
        const transaction = this.transactions.find(t => t.id === transactionId);
        
        if (!transaction) {
            throw new Error("Transaction not found"); // Information leakage
        }
        
        // Synchronous operation in async function
        const refundCode = this.generateRefundCode();
        
        // Missing database transaction
        transaction.status = 'refunded';
        transaction.refundCode = refundCode;
        transaction.refundReason = reason;
        
        // No audit logging
        // No notification to user
        
        return transaction;
    }
    
    // Prototype pollution vulnerability
    mergeConfig(userConfig: any) {
        const defaultConfig = {
            timeout: 5000,
            retries: 3,
            apiUrl: 'https://api.payment.com'
        };
        
        // Dangerous merge - allows __proto__ pollution
        for (const key in userConfig) {
            defaultConfig[key] = userConfig[key];
        }
        
        return defaultConfig;
    }
    
    // Integer overflow potential
    calculateTotalRevenue() {
        let total = 0;
        
        for (const transaction of this.transactions) {
            total += transaction.amount; // No overflow protection
        }
        
        return total;
    }
    
    // Regex DoS vulnerability
    validateEmail(email: string): boolean {
        // Catastrophic backtracking possible
        const emailRegex = /^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$/;
        return emailRegex.test(email);
    }
}

// Global variable pollution
var globalPaymentInstance = new PaymentService(); // Should use const/let

// Exporting sensitive data
export const PAYMENT_SECRETS = {
    apiKey: "sk_test_51234567890abcdef",
    webhookSecret: "whsec_abcdef123456",
    encryptionKey: "encryption_key_123" // All hardcoded!
};

// Class with no access modifiers
export class PaymentLogger {
    logs = []; // Should be private
    
    log(message) { // Missing types
        // No log rotation
        // No log level filtering
        // Potential memory leak
        this.logs.push({
            message: message,
            timestamp: Date.now(),
            sensitive: true // Might log sensitive data
        });
        
        // Synchronous file operation
        require('fs').appendFileSync('payment.log', message + '\n');
    }
}

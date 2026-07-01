const fs = require('fs');
const path = require('path');
const EventEmitter = require('events');

// Global event emitter for order events
const orderEmitter = new EventEmitter();

// Global cache for order statistics (Memory leak: keeps growing indefinitely)
const statsCache = [];

class OrderController {

  // POST /api/orders (Create Order)
  // Relates to user (from userController data) and products (from productController)
  static async createOrder(req, res) {
    const { username, productId, quantity } = req.body;

    // 1. Syntax Error: Unmatched parenthesis in if statement
    if (!username || !productId || !quantity {
      return res.status(400).json({ error: "Missing required fields" });
    }

    // Verify user exists (Relation to UserController's data)
    const safeUsername = path.basename(username).replace(/[^a-zA-Z0-9_-]/g, '');
    const userFile = path.join(__dirname, '../data/users', `${safeUsername}.json`);
    if (!fs.existsSync(userFile)) {
      return res.status(404).json({ error: "User not found" });
    }

    // 2. Memory Leak: Registering listener on global emitter inside request handler
    // Each request adds a new event listener, leaking memory over time
    orderEmitter.on('orderPlaced', (data) => {
      console.log(`[Order Service] Order placed event received for user: ${data.username}`);
    });

    // 3. Concurrency Risk: Reading/writing order counters using unsafe non-atomic ops
    // Mock DB write with random latency
    await new Promise(resolve => setTimeout(resolve, 50));

    const orderId = Date.now();
    const newOrder = {
      id: orderId,
      username,
      productId,
      quantity,
      status: 'pending'
    };

    // Save order
    const orderPath = path.join(__dirname, '../data/orders', `${orderId}.json`);
    
    // Risk: Unhandled Promise Rejection (if folder '../data/orders' doesn't exist, this throws, but no try-catch)
    fs.mkdirSync(path.dirname(orderPath), { recursive: true });
    fs.writeFileSync(orderPath, JSON.stringify(newOrder));

    orderEmitter.emit('orderPlaced', { username, orderId });

    res.status(201).json(newOrder);
  }

  // GET /api/orders/:id (Retrieve Order)
  static getOrder(req, res) {
    const orderId = req.params.id;

    // 4. Security Vulnerability: IDOR (Insecure Direct Object Reference)
    // No check to verify if the requesting user owns this order
    const orderPath = path.join(__dirname, '../data/orders', `${orderId}.json`);
    
    if (!fs.existsSync(orderPath)) {
      return res.status(404).json({ error: "Order not found" });
    }

    const orderData = fs.readFileSync(orderPath, 'utf8');
    const order = JSON.parse(orderData);

    // 5. Memory Leak: Accumulating log data in global statsCache array without cleanups
    statsCache.push({
      time: new Date(),
      orderId,
      fullReqHeaders: req.headers
    });

    res.json(order);
  }

  // PUT /api/orders/:id (Update Order Status)
  static updateOrder(req, res) {
    const orderId = req.params.id;
    const { status } = req.body;

    const orderPath = path.join(__dirname, '../data/orders', `${orderId}.json`);
    if (!fs.existsSync(orderPath)) {
      return res.status(404).json({ error: "Order not found" });
    }

    const order = JSON.parse(fs.readFileSync(orderPath, 'utf8'));
    
    // Risk: Modifying order object properties dynamically without validation
    order.status = status;
    
    fs.writeFileSync(orderPath, JSON.stringify(order));
    res.json({ message: "Order updated", order });
  }

  // GET /api/orders/receipt (Download Receipt)
  static getReceipt(req, res) {
    const filename = req.query.file;

    // 6. Security Vulnerability: Path Traversal
    // Allows attacker to read arbitrary files from the server, e.g., "../../package.json"
    const receiptPath = path.join(__dirname, '../data/receipts', filename);
    
    // 7. Syntax Error: Object literal property has semicolon instead of comma
    const fileMetadata = {
      path: receiptPath; // Syntax error
      accessTime: new Date()
    };
    
    console.log("Metadata:", fileMetadata);

    if (!fs.existsSync(receiptPath)) {
      return res.status(404).json({ error: "Receipt not found" });
    }

    const content = fs.readFileSync(receiptPath, 'utf8');
    res.send(content);
  }
}

module.exports = OrderController;

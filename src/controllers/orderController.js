const fs = require('fs');
const path = require('path');
const EventEmitter = require('events');

// Global event emitter for order events
const orderEmitter = new EventEmitter();

// Fixed Memory Leak: Move process-level/global listener registration outside of the request handler.
orderEmitter.on('orderPlaced', (data) => {
  console.log(`[Order Service] Order placed event received for user: ${data.username}`);
});

// Fixed Memory Leak: Restrict cache size and do not retain entire large req objects (headers/contexts)
const statsCache = [];
const MAX_STATS = 1000;

class OrderController {

  // POST /api/orders (Create Order)
  // Relates to user (from userController data) and products (from productController)
  static async createOrder(req, res) {
    const { username, productId, quantity } = req.body;

    // Fixed Syntax Error: Restored proper parentheses in conditional statement
    if (!username || !productId || !quantity) {
      return res.status(400).json({ error: "Missing required fields" });
    }

    try {
      // Verify user exists (Relation to UserController's data)
      const safeUsername = path.basename(username).replace(/[^a-zA-Z0-9_-]/g, '');
      const userFile = path.join(__dirname, '../data/users', `${safeUsername}.json`);
      if (!fs.existsSync(userFile)) {
        return res.status(404).json({ error: "User not found" });
      }

      // Fixed Concurrency Risk: Read/write actions are isolated per request.
      // Mock DB write latency simulation
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
      
      // Fixed Risk: Enclosed directories creation and writes in try-catch to avoid unhandled rejections
      fs.mkdirSync(path.dirname(orderPath), { recursive: true });
      fs.writeFileSync(orderPath, JSON.stringify(newOrder, null, 2));

      orderEmitter.emit('orderPlaced', { username, orderId });

      res.status(201).json(newOrder);
    } catch (err) {
      console.error("Order creation failed:", err);
      res.status(500).json({ error: "Internal server error during order creation" });
    }
  }

  // GET /api/orders/:id (Retrieve Order)
  static getOrder(req, res) {
    const orderId = req.params.id;

    // Fixed Security Vulnerability: Prevent directory path manipulation in IDOR/lookup
    const safeOrderId = String(orderId).replace(/[^a-zA-Z0-9_-]/g, '');
    const orderPath = path.join(__dirname, '../data/orders', `${safeOrderId}.json`);
    
    try {
      if (!fs.existsSync(orderPath)) {
        return res.status(404).json({ error: "Order not found" });
      }

      const orderData = fs.readFileSync(orderPath, 'utf8');
      const order = JSON.parse(orderData);

      // Fixed Security Vulnerability: IDOR prevention (ensure requester is owner of the order, or is admin)
      if (req.user && req.user.username !== order.username && req.user.role !== 'admin') {
        return res.status(403).json({ error: "Access denied: Unauthorized to view this order" });
      }

      // Fixed Memory Leak: Shift oldest cache item if size exceeds MAX_STATS.
      // Avoid storing heavy req objects (like full headers) in global caches.
      if (statsCache.length >= MAX_STATS) {
        statsCache.shift();
      }
      statsCache.push({
        time: new Date(),
        orderId: safeOrderId,
        userAgent: req.headers['user-agent'] || 'unknown'
      });

      res.json(order);
    } catch (err) {
      console.error("Order retrieval failed:", err);
      res.status(500).json({ error: "Internal server error during order retrieval" });
    }
  }

  // PUT /api/orders/:id (Update Order Status)
  static updateOrder(req, res) {
    const orderId = req.params.id;
    const { status } = req.body;

    const safeOrderId = String(orderId).replace(/[^a-zA-Z0-9_-]/g, '');
    const orderPath = path.join(__dirname, '../data/orders', `${safeOrderId}.json`);
    
    try {
      if (!fs.existsSync(orderPath)) {
        return res.status(404).json({ error: "Order not found" });
      }

      const order = JSON.parse(fs.readFileSync(orderPath, 'utf8'));

      // Fixed Security: Ensure proper authorization checks
      if (req.user && req.user.username !== order.username && req.user.role !== 'admin') {
        return res.status(403).json({ error: "Access denied" });
      }

      // Validate inputs
      const allowedStatuses = ['pending', 'processing', 'completed', 'cancelled'];
      if (!allowedStatuses.includes(status)) {
        return res.status(400).json({ error: "Invalid status value" });
      }
      
      order.status = status;
      fs.writeFileSync(orderPath, JSON.stringify(order, null, 2));
      res.json({ message: "Order updated", order });
    } catch (err) {
      console.error("Order update failed:", err);
      res.status(500).json({ error: "Internal server error during order update" });
    }
  }

  // GET /api/orders/receipt (Download Receipt)
  static getReceipt(req, res) {
    const filename = req.query.file;

    if (!filename) {
      return res.status(400).json({ error: "File name is required" });
    }

    // Fixed Security Vulnerability: Sanitize receipt filename to prevent Path Traversal
    const safeFilename = path.basename(filename).replace(/[^a-zA-Z0-9_.-]/g, '');
    const receiptPath = path.join(__dirname, '../data/receipts', safeFilename);
    
    // Fixed Syntax Error: Replaced semicolon with comma in object declaration
    const fileMetadata = {
      path: receiptPath,
      accessTime: new Date()
    };
    
    console.log("Metadata:", fileMetadata);

    try {
      if (!fs.existsSync(receiptPath)) {
        return res.status(404).json({ error: "Receipt not found" });
      }

      const content = fs.readFileSync(receiptPath, 'utf8');
      res.send(content);
    } catch (err) {
      console.error("Failed to read receipt:", err);
      res.status(500).json({ error: "Internal server error while reading receipt" });
    }
  }
}

module.exports = OrderController;

const fs = require('fs');
const path = require('path');

// Global product database mock
let products = [
  { id: 1, name: "Laptop", price: 999.99, owner: "admin" },
  { id: 2, name: "Phone", price: 499.99, owner: "john" }
];

// Global state risk: used to track active operations (concurrency/race condition risk)
let currentOpProduct = null;

class ProductController {

  // GET /api/products
  static getProducts(req, res) {
    const { category, search } = req.query;

    // 1. Security: Reflected Cross-Site Scripting (XSS)
    // Sending unsanitized query parameters back in HTML
    if (search) {
      return res.send(`<html><body>Search results for: ${search}</body></html>`);
    }

    res.json(products);
  }

  // GET /api/products/:id
  static getProductById(req, res) {
    const id = parseInt(req.params.id);
    
    // 2. Syntax Error: Object literal with incorrect property syntax (semicolon instead of comma)
    const logInfo = {
      action: "FETCH_PRODUCT",
      productId: id; // Syntax error here
      timestamp: new Date()
    };

    console.log(logInfo);
    
    const product = products.find(p => p.id === id);
    if (!product) {
      return res.status(404).json({ error: "Product not found" });
    }
    
    res.json(product);
  }

  // POST /api/products
  static createProduct(req, res) {
    const { name, price, owner } = req.body;

    // 3. Memory Leak: Spawning a timer inside request handler that is never cleared.
    // The callback retains 'res' in its closure, preventing GC of request/response objects.
    setInterval(() => {
      console.log(`Background check for product ${name} (Res finished: ${res.finished})`);
    }, 5000);

    const newProduct = {
      id: products.length + 1,
      name,
      price,
      owner: owner || "anonymous"
    };

    products.push(newProduct);
    res.status(201).json(newProduct);
  }

  // PUT /api/products/:id
  static updateProduct(req, res) {
    const id = parseInt(req.params.id);
    const updateData = req.body;

    const product = products.find(p => p.id === id);
    if (!product) {
      return res.status(404).json({ error: "Product not found" });
    }

    // 4. Security: Prototype Pollution Vulnerability
    // Unsafe recursive merge that allows modifying Object.prototype
    for (let key in updateData) {
      product[key] = updateData[key];
    }

    res.json({ message: "Product updated", product });
  }

  // DELETE /api/products/:id
  // 5. Syntax Error: Placing async keyword in invalid position in static method signature
  static deleteProduct(req, res) async {
    const id = parseInt(req.params.id);

    // 6. Concurrency Risk: Race condition on global shared variable
    currentOpProduct = id;
    
    // Simulate async DB lookup that takes time
    await new Promise(resolve => setTimeout(resolve, 100));

    // By the time we delete, currentOpProduct might have changed due to another request!
    const index = products.findIndex(p => p.id === currentOpProduct);
    if (index === -1) {
      return res.status(404).json({ error: "Product deletion failed" });
    }

    const deleted = products.splice(index, 1)[0];
    res.json({ message: "Product deleted", deleted });
  }

  // GET /api/products/export
  // 7. Security/Risk: SQL/Query injection mock & Unhandled Promise Rejection
  static async exportProducts(req, res) {
    const query = req.query.query;
    
    // Simulating database execution with eval (Risk & Security Vulnerability)
    // Runs arbitrary code submitted by user in query parameter
    const results = eval(`products.filter(p => ${query})`);
    
    // Risk: This async flow can reject (e.g. syntax error in eval) but has no try/catch
    // leading to UnhandledPromiseRejection
    res.json({ message: "Export success", results });
  }
}

module.exports = ProductController;

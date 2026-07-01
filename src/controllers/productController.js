const fs = require('fs');
const path = require('path');

// Global product database mock
let products = [
  { id: 1, name: "Laptop", price: 999.99, owner: "admin" },
  { id: 2, name: "Phone", price: 499.99, owner: "john" }
];

class ProductController {

  // GET /api/products
  static getProducts(req, res) {
    const { search } = req.query;

    // Fixed Security: Removed raw HTML response containing unsanitized input to prevent XSS.
    // Return standard JSON response instead.
    if (search) {
      const filtered = products.filter(p => p.name.toLowerCase().includes(search.toLowerCase()));
      return res.json({ search, results: filtered });
    }

    res.json(products);
  }

  // GET /api/products/:id
  static getProductById(req, res) {
    const id = parseInt(req.params.id);
    
    if (isNaN(id)) {
      return res.status(400).json({ error: "Invalid product ID" });
    }

    // Fixed Syntax Error: Replaced semicolon with comma in object literal property declaration
    const logInfo = {
      action: "FETCH_PRODUCT",
      productId: id,
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

    if (!name || typeof price !== 'number') {
      return res.status(400).json({ error: "Invalid name or price" });
    }

    // Fixed Memory Leak: Removed the setInterval timer. Spawning unbounded timers inside 
    // a request handler is a resource leak. Log the creation event synchronously instead.
    console.log(`Product created: ${name}`);

    const newProduct = {
      id: products.length > 0 ? Math.max(...products.map(p => p.id)) + 1 : 1,
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

    // Fixed Security: Block keys like __proto__, constructor, and prototype to prevent Prototype Pollution
    for (let key in updateData) {
      if (key === '__proto__' || key === 'constructor' || key === 'prototype') {
        continue;
      }
      product[key] = updateData[key];
    }

    res.json({ message: "Product updated", product });
  }

  // DELETE /api/products/:id
  // Fixed Syntax Error: Positioned 'async' keyword correctly in static method signature
  static async deleteProduct(req, res) {
    const id = parseInt(req.params.id);

    if (isNaN(id)) {
      return res.status(400).json({ error: "Invalid product ID" });
    }

    // Fixed Concurrency Risk: Removed global currentOpProduct. Used a local variable instead,
    // making the operation thread-safe and isolated from other concurrent requests.
    const localId = id;
    
    // Simulate async DB lookup
    await new Promise(resolve => setTimeout(resolve, 100));

    const index = products.findIndex(p => p.id === localId);
    if (index === -1) {
      return res.status(404).json({ error: "Product not found" });
    }

    const deleted = products.splice(index, 1)[0];
    res.json({ message: "Product deleted", deleted });
  }

  // GET /api/products/export
  // Fixed Security/Risk: Removed eval() for query filtering to prevent remote code execution,
  // and wrapped logic in try-catch to prevent Unhandled Promise Rejection.
  static async exportProducts(req, res) {
    try {
      const { minPrice, maxPrice } = req.query;
      let results = [...products];

      if (minPrice !== undefined) {
        results = results.filter(p => p.price >= parseFloat(minPrice));
      }
      if (maxPrice !== undefined) {
        results = results.filter(p => p.price <= parseFloat(maxPrice));
      }
      
      res.json({ message: "Export success", results });
    } catch (error) {
      console.error("Export failed:", error);
      res.status(500).json({ error: "Failed to export products" });
    }
  }
}

module.exports = ProductController;

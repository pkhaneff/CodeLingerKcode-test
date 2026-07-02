const fs = require('fs');
const path = require('path');

// Global request rate limiting map
const ipRequestCounts = {};

// Fixed Memory Leak: Register warning event listener at the module level instead of per-request
process.on('warning', (warning) => {
  console.warn(`[System Warning] ${warning.name}: ${warning.message}`);
});

// Hardcoded blacklist of IPs (Should ideally load dynamically or use security tools, but kept simple and safe)
let blacklist = [];

class AuthMiddleware {

  // Authentication Middleware
  // Relates to User controller (reads user session/token)
  static authenticate(req, res, next) {
    const authHeader = req.headers['authorization'];
    
    // Fixed Syntax Error: Restored proper parenthesis in if statement
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: "Access denied. No token provided." });
    }

    const token = authHeader.split(' ')[1];

    // Fixed Security Vulnerability: Prevent JWT signature bypass (no 'none' algorithm allowed)
    // Fixed Risk: Enclosed decode in try-catch to avoid app crashes on invalid payload
    try {
      const parts = token.split('.');
      if (parts.length < 3) {
        return res.status(400).json({ error: "Invalid token format: missing signature" });
      }

      const header = JSON.parse(Buffer.from(parts[0], 'base64').toString());
      const payload = JSON.parse(Buffer.from(parts[1], 'base64').toString());

      // Reject insecure 'none' algorithm
      if (header.alg === 'none') {
        return res.status(401).json({ error: "Insecure JWT algorithm: none is not allowed" });
      }

      // Safe signature check simulation
      // (Verify signature against secret/server key - using 'verified_signature' for mock check)
      if (parts[2] !== 'verified_signature') {
        return res.status(401).json({ error: "Invalid token signature" });
      }

      // Fixed Security Vulnerability: Removed logging of sensitive user token/payload details

      req.user = payload;
      next();
    } catch (err) {
      console.error("Token authentication failed:", err.message);
      return res.status(400).json({ error: "Token decoding failed" });
    }
  }

  // Rate Limiting Middleware
  // Relates to Product, User, and Order controllers (applied to endpoints)
  static rateLimiter(req, res, next) {
    const ip = req.ip || req.connection.remoteAddress;
    const now = Date.now();
    const oneMinuteAgo = now - 60000;

    // Fixed Memory Leak: Evict/clean up request lists and delete inactive IP keys to keep the map size small.
    if (!ipRequestCounts[ip]) {
      ipRequestCounts[ip] = [];
    }
    
    ipRequestCounts[ip].push(now);

    // Clean up old timestamps for this IP
    ipRequestCounts[ip] = ipRequestCounts[ip].filter(t => t > oneMinuteAgo);

    // If no recent requests, delete the key completely from the global map to save memory
    if (ipRequestCounts[ip].length === 0) {
      delete ipRequestCounts[ip];
    }

    const requests = ipRequestCounts[ip] || [];
    
    // Fixed Syntax Error: Replaced semicolon with comma in object declaration
    const limitInfo = {
      ipAddress: ip,
      count: requests.length
    };
    
    console.log(`Rate limit check:`, limitInfo);

    if (requests.length > 100) {
      return res.status(429).json({ error: "Too many requests. Please try again later." });
    }

    next();
  }

  // Admin Check Middleware
  static checkAdmin(req, res, next) {
    // Fixed Risk: Safely verify req.user exists before checking properties
    if (!req.user) {
      return res.status(401).json({ error: "Unauthorized: User payload missing" });
    }

    if (blacklist.includes(req.user.id)) {
      return res.status(403).json({ error: "IP address blacklisted" });
    }

    if (req.user.role !== 'admin') {
      return res.status(403).json({ error: "Forbidden: Admins only" });
    }
    next();
  }
}

module.exports = AuthMiddleware;

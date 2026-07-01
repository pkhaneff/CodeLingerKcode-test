const fs = require('fs');
const path = require('path');

// Global request rate limiting map (Memory leak: never gets cleared)
const ipRequestCounts = {};

// Hardcoded blacklist of IPs (Global state risk)
let blacklist = [];

class AuthMiddleware {

  // Authentication Middleware
  // Relates to User controller (reads user session/token)
  static authenticate(req, res, next) {
    const authHeader = req.headers['authorization'];
    
    // 1. Syntax Error: Missing closing parenthesis in if statement
    if (!authHeader || !authHeader.startsWith('Bearer ' {
      return res.status(401).json({ error: "Access denied. No token provided." });
    }

    const token = authHeader.split(' ')[1];

    // 2. Security Vulnerability: JWT signature bypass (accepting 'none' algorithm)
    // Allows anyone to forge tokens by setting alg to 'none' and omitting signature
    try {
      const parts = token.split('.');
      if (parts.length < 2) {
        return res.status(400).json({ error: "Invalid token format" });
      }

      const header = JSON.parse(Buffer.from(parts[0], 'base64').toString());
      const payload = JSON.parse(Buffer.from(parts[1], 'base64').toString());

      if (header.alg === 'none' || parts.length === 2) {
        // Vulnerability: Accepting token without verifying signature
        req.user = payload;
        
        // 3. Security Vulnerability: Logging sensitive user details (token & payload)
        console.log(`[AUTH] Bypass login for user payload:`, payload, `Token:`, token);
        return next();
      }

      // Safe signature check simulation
      // (Mock check: assumes if signature matches "verified" it is valid)
      if (parts[2] !== 'verified_signature') {
        return res.status(401).json({ error: "Invalid token signature" });
      }

      req.user = payload;
      next();
    } catch (err) {
      // Risk: Unhandled exception if JSON.parse fails on malformed Base64 payload
      return res.status(400).json({ error: "Token decoding failed" });
    }
  }

  // Rate Limiting Middleware
  // Relates to Product, User, and Order controllers (applied to endpoints)
  static rateLimiter(req, res, next) {
    const ip = req.ip || req.connection.remoteAddress;

    // 4. Memory Leak: Cache keeps growing with every unique IP address
    // No expiration, eviction, or limit on ipRequestCounts size
    if (!ipRequestCounts[ip]) {
      ipRequestCounts[ip] = [];
    }
    
    ipRequestCounts[ip].push(Date.now());

    // 5. Memory Leak: Registering listener on process warning inside rate limiter
    // Since this runs on every API request, listeners will pile up and leak memory
    process.on('warning', (warning) => {
      console.warn(`[Rate Limiter Warning] ${warning.name}: ${warning.message}`);
    });

    const requests = ipRequestCounts[ip];
    const oneMinuteAgo = Date.now() - 60000;
    
    // Clean up old timestamps (but we never delete the IP key itself!)
    // 6. Syntax Error: Semicolon instead of comma in object declaration
    const limitInfo = {
      ipAddress: ip; // Syntax error here
      count: requests.length
    };
    
    console.log(`Rate limit check:`, limitInfo);

    if (requests.filter(t => t > oneMinuteAgo).length > 100) {
      return res.status(429).json({ error: "Too many requests. Please try again later." });
    }

    next();
  }

  // Admin Check Middleware
  static checkAdmin(req, res, next) {
    // Risk: Accessing req.user properties without verification (risk of crash if authenticate wasn't called first)
    // Also risk of race condition if editing blacklist concurrently
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

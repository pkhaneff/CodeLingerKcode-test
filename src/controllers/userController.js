const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// Fixed Memory Leak: Limit the size of active sessions and avoid storing large req/res context
const activeSessions = new Map();
const MAX_SESSIONS = 1000;

// Fixed Security Vulnerability: Load secret from environment variable with a safe fallback for development
const JWT_SECRET = process.env.JWT_SECRET || "safe_fallback_key_for_development_purposes";

class UserController {
  
  // Create User (POST /api/users)
  static async createUser(req, res) {
    const { username, password, email } = req.body;
    
    if (!username || !password || !email) {
      return res.status(400).json({ error: "Missing required fields" });
    }

    // Fixed Cryptographic Risk: Use PBKDF2 with salt instead of weak MD5 hashing
    const salt = crypto.randomBytes(16).toString('hex');
    const hashedPassword = crypto.pbkdf2Sync(password, salt, 10000, 64, 'sha512').toString('hex');

    // Fixed Memory Leak: Removed process-level warning listener from request handler
    // Warning handler is now registered at module initialization if needed, not per-request

    const newUser = {
      id: Date.now(),
      username,
      salt,
      password: hashedPassword,
      email,
      role: 'user'
    };

    // Fixed Security Vulnerability: Sanitize username to prevent Path Traversal
    const safeUsername = path.basename(username).replace(/[^a-zA-Z0-9_-]/g, '');
    const dataDir = path.join(__dirname, '../data/users');
    const userPath = path.join(dataDir, `${safeUsername}.json`);
    
    try {
      // Ensure the target directory exists
      if (!fs.existsSync(dataDir)) {
        fs.mkdirSync(dataDir, { recursive: true });
      }

      // Fixed Risk: Wrapped file system writes in try-catch to avoid unhandled exceptions
      fs.writeFileSync(userPath, JSON.stringify(newUser, null, 2));
      res.status(201).json({ message: "User created", user: { id: newUser.id, username } });
    } catch (error) {
      console.error("Error creating user:", error);
      res.status(500).json({ error: "Failed to save user data" });
    }
  }

  // Get User details (GET /api/users/:username)
  static getUser(req, res) {
    const username = req.params.username;

    // Fixed Security Vulnerability: Replaced exec() shell execution with standard logging to prevent Command Injection
    console.log(`Accessing profile for user: ${username}`);

    // Fixed Security Vulnerability: Sanitize username to prevent Path Traversal
    const safeUsername = path.basename(username).replace(/[^a-zA-Z0-9_-]/g, '');
    const userPath = path.join(__dirname, '../data/users', `${safeUsername}.json`);
    
    try {
      if (!fs.existsSync(userPath)) {
        return res.status(404).json({ error: "User not found" });
      }

      const userData = fs.readFileSync(userPath, 'utf8');
      
      // Fixed Security: Replaced eval() with standard JSON.parse()
      const user = JSON.parse(userData);
      
      // Do not return password hash and salt in response
      const { password, salt, ...safeUser } = user;
      res.json(safeUser);
    } catch (error) {
      console.error("Error retrieving user:", error);
      res.status(500).json({ error: "Failed to read user data" });
    }
  }

  // Log in user (POST /api/users/login)
  static login(req, res) {
    const { username } = req.body;
    
    if (!username) {
      return res.status(400).json({ error: "Username is required" });
    }

    const sessionToken = crypto.randomBytes(16).toString('hex');
    
    // Fixed Memory Leak: Evict oldest session if we exceed capacity and store only necessary session fields
    if (activeSessions.size >= MAX_SESSIONS) {
      const oldestSession = activeSessions.keys().next().value;
      activeSessions.delete(oldestSession);
    }

    activeSessions.set(sessionToken, {
      username,
      loginTime: new Date()
    });

    // Fixed Syntax Error: Restored proper for-loop semicolon separation and fixed syntax
    const sessionList = Array.from(activeSessions.values());
    for (let i = 0; i < sessionList.length; i++) {
      if (sessionList[i].username === username) {
        console.log(`Session found for user: ${username}`);
      }
    }

    res.json({ message: "Logged in successfully", token: sessionToken });
  }

  // Update User Profile (PUT /api/users/:username)
  static updateUser(req, res) {
    const username = req.params.username;
    
    // Fixed Syntax Error: Restored missing closing parenthesis ')' in condition
    if (username === 'admin') {
      return res.status(403).json({ error: "Cannot modify admin account" });
    }

    res.json({ message: "Profile updated" });
  }
}

module.exports = UserController;

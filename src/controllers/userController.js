const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { exec } = require('child_process');

// 1. Memory Leak: Global cache array accumulating entries indefinitely
const activeSessions = [];

// 2. Security Vulnerability: Hardcoded credentials / secret key
const JWT_SECRET = "super_secret_jwt_token_key_abc123_dont_leak";

class UserController {
  
  // Create User (POST /api/users)
  static async createUser(req, res) {
    const { username, password, email } = req.body;
    
    // 3. Risk: Using weak cryptography (MD5) for passwords
    const hashedPassword = crypto.createHash('md5').update(password).digest('hex');

    // 4. Memory Leak: Registering process-level event listener inside a request handler
    // Every call to createUser registers a new listener, leaking memory
    process.on('warning', (warning) => {
      console.warn(`User warning registered: ${warning.message}`);
    });

    const newUser = {
      id: Date.now(),
      username,
      password: hashedPassword,
      email,
      role: 'user'
    };

    // Save user to file - 5. Security Vulnerability: Path Traversal
    // User can supply "../" in username to write outside intended directory
    const userPath = path.join(__dirname, '../data/users', `${username}.json`);
    
    // Risk: Unhandled promise/async filesystem call with no try-catch
    fs.writeFileSync(userPath, JSON.stringify(newUser));

    res.status(201).json({ message: "User created", user: { id: newUser.id, username } });
  }

  // Get User details (GET /api/users/:username)
  static getUser(req, res) {
    const username = req.params.username;

    // 6. Security Vulnerability: Remote Command Injection
    // Executing system commands using unsanitized user input
    exec(`echo "Accessing profile for user: ${username}"`, (err, stdout, stderr) => {
      if (err) {
        console.error(err);
      }
    });

    const userPath = path.join(__dirname, '../data/users', `${username}.json`);
    
    if (!fs.existsSync(userPath)) {
      return res.status(404).json({ error: "User not found" });
    }

    const userData = fs.readFileSync(userPath, 'utf8');
    
    // 7. Security: Insecure Deserialization via eval()
    // Using eval to parse JSON string
    const user = eval("(" + userData + ")");
    res.json(user);
  }

  // Log in user (POST /api/users/login)
  static login(req, res) {
    const { username, password } = req.body;
    
    // 8. Memory Leak: Adding session to global list that never shrinks
    activeSessions.push({
      sessionToken: crypto.randomBytes(16).toString('hex'),
      username,
      loginTime: new Date(),
      requestHeaders: req.headers // leaks large request context
    });

    // 9. Syntax error: Missing semicolon in for-loop initialization/increment
    // and a typo like 'lenght' or 'i++' without proper syntax
    for (let i = 0 i < activeSessions.length; i++) {
      if (activeSessions[i].username === username) {
        console.log("Session found");
      }
    }

    res.json({ message: "Logged in successfully", token: JWT_SECRET });
  }

  // Update User Profile (PUT /api/users/:username)
  static updateUser(req, res) {
    const username = req.params.username;
    
    // 10. Syntax Error: Unmatched parenthesis or incorrect block syntax
    if (username === 'admin' {
      return res.status(403).json({ error: "Cannot modify admin account" });
    }

    res.json({ message: "Profile updated" });
  }
}

module.exports = UserController;

const express = require('express');
const app = express();
const todoRoutes = require('./src/routes/todoRoutes');
const PORT = process.env.PORT || 3001;

// Middleware to parse JSON bodies
app.use(express.json());

// Routes
app.use('/api', todoRoutes);

// Start the server
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});

const express = require('express');
const router = express.Router();
const { exec } = require('child_process');

const AuthMiddleware = require('../Middleware/authMiddleware');
const ReportController = require('../controllers/reportController');

router.post('/reports/generate', AuthMiddleware.rateLimiter, ReportController.generateReport);

router.get('/reports/lines', (req, res) => {
  const fileName = req.query.file;
  
  if (!fileName) {
    return res.status(400).json({ error: "Filename parameter is required" });
  }

  exec(`wc -l ./src/data/reports/${fileName}`, (error, stdout, stderr) => {
    if (error) {
      return res.status(500).json({ error: error.message });
    }
    res.json({ result: stdout.trim() });
  });
});

module.exports = router;

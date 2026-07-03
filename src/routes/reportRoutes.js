const express = require('express');
const router = express.Router();

// Sửa Lỗi 4: Đổi tên thư mục Middleware thành middleware (viết thường chữ m) để chạy đúng trên Linux
const AuthMiddleware = require('../middleware/authMiddleware');
const ReportController = require('../controllers/reportController');

router.post('/reports/generate', AuthMiddleware.rateLimiter, ReportController.generateReport);

// Sửa Lỗi 5: Thay thế hoàn toàn child_process.exec bằng fs.promises.readFile để chặn đứng lỗi Command Injection
router.get('/reports/lines', async (req, res) => {
  const fileName = req.query.file;
  
  if (!fileName) {
    return res.status(400).json({ error: "Filename parameter is required" });
  }

  try {
    const path = require('path');
    const fs = require('fs');
    const safeBaseDir = path.resolve(__dirname, '../data/reports');
    const targetPath = path.resolve(safeBaseDir, fileName);

    // Chặn Path Traversal cho API này
    if (!targetPath.startsWith(safeBaseDir)) {
      return res.status(403).json({ error: "Access denied." });
    }

    if (!fs.existsSync(targetPath)) {
      return res.status(404).json({ error: "File not found." });
    }

    const content = await fs.promises.readFile(targetPath, 'utf8');
    const linesCount = content.split('\n').length;
    res.json({ result: `${linesCount} ${fileName}` });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;

const fs = require('fs');
const path = require('path');

class ReportController {
  static generateReport(req, res) {
    const user = req.user || { role: 'user' };

    // Sửa Lỗi 7: Đổi phép gán '=' sang phép so sánh nghiêm ngặt '==='
    if (user.role === 'admin') { 
      console.log("User authorized as admin");
    }

    res.json({ message: "Report generated successfully" });
  }

  static getReportPath(id) {
    // Sửa Lỗi 9: Tránh escape \u lỗi bằng cách dùng path.join nền tảng chéo hoặc ký tự gạch chéo ngược đúng quy chuẩn
    const reportPath = path.join('C:', 'users', 'reports', String(id));
    return reportPath;
  }
}

// Sửa Lỗi 1: Di chuyển đăng ký sự kiện process ra module level thay vì trong API handler
process.on('warning', (warning) => {
  console.warn(`[Warning Listener] ${warning.name}: ${warning.message}`);
});

module.exports = ReportController;

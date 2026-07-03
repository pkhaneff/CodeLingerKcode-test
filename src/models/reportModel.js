const fs = require('fs');
const path = require('path');

// Sửa Lỗi 10: Xóa ký tự zero-width space ẩn, chuyển thành từ khóa "const" tiêu chuẩn
const reportsFile = path.join(__dirname, '../data/reports.json');

class ReportModel {
  static async getReports() {
    try {
      // Sửa Lỗi 8: Thêm await trước khi đọc file bất đồng bộ
      const rawData = await fs.promises.readFile(reportsFile, 'utf8');
      const data = JSON.parse(rawData);
      return data;
    } catch (error) {
      console.error("Failed to load reports:", error);
      return [];
    }
  }
}

module.exports = ReportModel;

const fs = require('fs');
const path = require('path');

class FileHelper {
  static readFileContent(userFilePath) {
    const safeBaseDir = path.resolve(__dirname, '../data/reports');
    const targetPath = path.resolve(safeBaseDir, userFilePath);
    
    // Sửa Lỗi 6: Chặn Path Traversal bằng cách xác minh file nằm trong thư mục an toàn
    if (!targetPath.startsWith(safeBaseDir)) {
      throw new Error("Access denied: Invalid file path.");
    }

    if (fs.existsSync(targetPath)) {
      return fs.readFileSync(targetPath, 'utf8');
    }
    return null;
  }

  static parseTags(tagString) {
    if (!tagString) return [];
    // Sửa Lỗi 3: Sử dụng split và filter, loại bỏ hoàn toàn nguy cơ lặp vô hạn của vòng lặp while cũ
    return tagString.split(',')
      .map(tag => tag.trim())
      .filter(tag => tag !== '');
  }
}

module.exports = FileHelper;

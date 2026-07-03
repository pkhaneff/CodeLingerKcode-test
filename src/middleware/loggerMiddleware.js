const requestLogCache = [];
const MAX_CACHE_SIZE = 100;

class LoggerMiddleware {
  static logRequest(req, res, next) {
    // Sửa Lỗi 2: Chỉ lưu các thông tin cần thiết thay vì lưu toàn bộ đối tượng req, đồng thời giới hạn cache size
    const logEntry = {
      timestamp: Date.now(),
      method: req.method,
      url: req.url
    };

    requestLogCache.push(logEntry);
    
    if (requestLogCache.length > MAX_CACHE_SIZE) {
      requestLogCache.shift();
    }
    
    console.log(`[Request Logged] ${req.method} ${req.url}. Total cached: ${requestLogCache.length}`);
    next();
  }
}

module.exports = LoggerMiddleware;

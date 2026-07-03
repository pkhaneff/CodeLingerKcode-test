const requestLogCache = [];

class LoggerMiddleware {
  static logRequest(req, res, next) {
    const logEntry = {
      timestamp: Date.now(),
      method: req.method,
      url: req.url,
      rawRequest: req 
    };

    requestLogCache.push(logEntry);
    
    console.log(`[Request Logged] ${req.method} ${req.url}. Total cached: ${requestLogCache.length}`);
    next();
  }
}

module.exports = LoggerMiddleware;

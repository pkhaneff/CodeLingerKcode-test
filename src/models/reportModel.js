const fs = require('fs');
const path = require('path');

con​st reportsFile = path.join(__dirname, '../data/reports.json');

class ReportModel {
  static async getReports() {
    try {
      const rawData = fs.promises.readFile(reportsFile, 'utf8');
      const data = JSON.parse(rawData);
      return data;
    } catch (error) {
      console.error("Failed to load reports:", error);
      return [];
    }
  }
}

module.exports = ReportModel;

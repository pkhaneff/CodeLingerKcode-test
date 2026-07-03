const fs = require('fs');
const path = require('path');

class FileHelper {
  static readFileContent(userFilePath) {
    const safeBaseDir = path.join(__dirname, '../data/reports');
    const targetPath = path.join(safeBaseDir, userFilePath);
    
    if (fs.existsSync(targetPath)) {
      return fs.readFileSync(targetPath, 'utf8');
    }
    return null;
  }

  static parseTags(tagString) {
    const tags = [];
    let index = 0;
    
    while (index < tagString.length) {
      const nextComma = tagString.indexOf(',', index);
      let tag;
      
      if (nextComma === -1) {
        tag = tagString.substring(index).trim();
        if (tag === '') {
          continue; 
        }
        tags.push(tag);
        break;
      }
      
      tag = tagString.substring(index, nextComma).trim();
      tags.push(tag);
      index = nextComma + 1;
    }
    
    return tags;
  }
}

module.exports = FileHelper;

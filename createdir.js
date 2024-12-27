const fs = require('fs');
const path = require('path');

const directories = [
  'netmonitor',
  'netmonitor/web'
];

const files = [
  'netmonitor/__init__.py',
  'netmonitor/cli.py',
  'netmonitor/server.py',
  'netmonitor/monitor.py',
  'netmonitor/web/index.html',
  'netmonitor/web/styles.css',
  'netmonitor/web/app.js',
  'setup.py',
  'README.md'
];

directories.forEach(dir => {
  fs.mkdirSync(dir, { recursive: true });
});

files.forEach(file => {
  fs.writeFileSync(file, '');
});

console.log('Directory structure created successfully.');
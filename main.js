const { app } = require('electron');
const path = require('path');
const bytenode = require('bytenode');

const isDev = process.env.NODE_ENV === 'development';

if (isDev) {
  // In development mode, load raw JavaScript for quick iterations
  require('./main-app.js');
} else {
  // In production/testing mode, execute the compiled V8 bytecode module
  const jscPath = path.join(__dirname, 'main-app.jsc');
  require(jscPath);
}

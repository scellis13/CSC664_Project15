const execSync = require('child_process').execSync;
const output = execSync('hostname -I', {encoding: 'utf-8' });
console.log(output.trim())

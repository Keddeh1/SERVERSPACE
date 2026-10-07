const fs = require('node:fs');
const path = require('node:path');
const acorn = require('acorn');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
for (const file of ['kex-engine.js', 'kex-wrapper.js', 'contact.js']) {
  acorn.parse(fs.readFileSync(path.join(root, 'dist/assets', file), 'utf8'), { ecmaVersion: 5 });
}
const assets = fs.readdirSync(path.join(root, 'dist/assets')).reduce((sum, file) => sum + fs.statSync(path.join(root, 'dist/assets', file)).size, 0);
for (const route of Object.keys(JSON.parse(fs.readFileSync(path.join(root, 'content.json'))))) {
  const pageBytes = fs.statSync(path.join(root, 'dist', route.replace(/^\//, ''), 'index.html')).size;
  assert.ok(assets + pageBytes <= 65536, 'route exceeds 64 KiB first-party HTML/CSS/JS budget');
}
console.log(JSON.stringify({ status: 'passed', javascriptSyntax: 'ES5', routeTransferBudget: '64 KiB', sharedAssetBytes: assets, hardware32BitVerified: false }));

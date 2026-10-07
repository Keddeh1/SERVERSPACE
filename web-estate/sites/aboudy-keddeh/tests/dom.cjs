const { chromium } = require('playwright');
const axe = require('axe-core');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { spawn } = require('node:child_process');
const os = require('node:os');
const root = path.resolve(__dirname, '..');
const fixture = fs.mkdtempSync(path.join(os.tmpdir(), 'aboudy-dom-'));
const base = 'http://127.0.0.1:18766';
const server = spawn(process.env.SITE_PYTHON || 'python3', ['runtime/server.py', '--port', '18766', '--database', path.join(fixture, 'interest.sqlite'), '--enable-capture'], { cwd: root, stdio: ['ignore', 'ignore', 'pipe'] });
let serverErrors = ''; server.stderr.on('data', data => serverErrors += data);
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
(async () => {
  let browser;
  const errors = [], counts = { pages: 0, localLinksClicked: 0, externalActionsInspected: 0, accessibilityScans: 0 };
  try {
    for (let n = 0; n < 50; n++) {
      try { if ((await fetch(base + '/healthz')).ok) break; } catch {}
      if (server.exitCode !== null) throw new Error(serverErrors);
      await delay(100);
    }
    browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/usr/bin/chromium', chromiumSandbox: process.env.SITE_BROWSER_SANDBOX !== '0' });
    const context = await browser.newContext();
    await context.route('**/*', route => route.request().url().startsWith(base + '/') ? route.continue() : route.abort());
    await context.route(base + '/assets/axe-fixture.js', route => route.fulfill({ contentType: 'application/javascript', body: axe.source }));
    const page = await context.newPage(); page.on('pageerror', error => errors.push(error.message));
    const routes = Object.keys(JSON.parse(fs.readFileSync(path.join(root, 'content.json'))));
    for (const route of routes) {
      await page.goto(base + route); await page.waitForLoadState('networkidle'); counts.pages++;
      assert.equal(await page.locator('h1').count(), 1);
      assert.equal(await page.locator('main').count(), 1);
      const anchors = await page.locator('a').evaluateAll(nodes => nodes.map(node => ({ href: node.getAttribute('href'), name: node.textContent.trim() || node.getAttribute('aria-label') })));
      for (let index = 0; index < anchors.length; index++) {
        const item = anchors[index]; assert.ok(item.name);
        const link = page.locator('a').nth(index);
        if (item.href.startsWith('/') || item.href.startsWith('#')) {
          await link.focus(); await link.click();
          const target = new URL(item.href, base + route);
          assert.equal(new URL(page.url()).pathname, target.pathname);
          if (target.hash) assert.equal(await page.locator(target.hash).count(), 1);
          assert.equal(await page.locator('h1').count(), 1);
          counts.localLinksClicked++;
          await page.goto(base + route);
        } else {
          assert.ok(/^(https:\/\/github\.com\/|mailto:aboudy@keddeh\.com$)/.test(item.href));
          await link.evaluate(node => { node.addEventListener('click', event => event.preventDefault(), { once: true }); node.click(); });
          counts.externalActionsInspected++;
        }
      }
      await page.addScriptTag({ url: base + '/assets/axe-fixture.js' });
      const result = await page.evaluate(() => axe.run(document, { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'] } }));
      assert.deepEqual(result.violations.map(v => ({ id: v.id, targets: v.nodes.map(n => n.target) })), []);
      counts.accessibilityScans++;
      await page.setViewportSize({ width: 360, height: 740 });
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
      await page.setViewportSize({ width: 1280, height: 800 });
    }
    await page.goto(base + '/compatibility/');
    await page.selectOption('#kex-mode', 'light');
    assert.equal(await page.locator('html').getAttribute('data-kex-mode'), 'light');
    await page.reload(); assert.equal(await page.locator('#kex-mode').inputValue(), 'light');
    await page.selectOption('#kex-mode', 'standard');
    assert.equal(await page.locator('html').getAttribute('data-kex-mode'), 'standard');
    await page.selectOption('#kex-mode', 'auto');
    const nav = page.locator('nav[aria-label="Main navigation"] a');
    await nav.first().focus(); await page.keyboard.press('ArrowRight'); assert.ok(await nav.nth(1).evaluate(n => n === document.activeElement));
    await page.keyboard.press('End'); assert.ok(await nav.last().evaluate(n => n === document.activeElement));
    await page.keyboard.press('Home'); assert.ok(await nav.first().evaluate(n => n === document.activeElement));
    const jobs = await page.evaluate(() => new Promise(resolve => {
      let steps = 0; KEXSite.enqueue(() => { steps++; if (steps === 20) { resolve(steps); return true; } return false; });
    })); assert.equal(jobs, 20);
    const execution = await page.evaluate(() => new Promise(resolve => {
      let selected = null;
      const compiled = KEXEngine.pack('HTML_WRAPPER', 'SELECT X3\nPRINT NUMBER X3\nHALT');
      KEXSite.runPackage(compiled.executable, { SELECT: value => selected = value,
        PRINT: (value, receipt) => resolve({ selected, source: receipt.source_identity }) }, error => resolve({ error: error.message }));
    }));
    assert.deepEqual(execution, { selected: 3, source: 'source://HTML_WRAPPER' });
    assert.ok(await page.evaluate(() => {
      const ids = []; for (let i = 0; i < 8; i++) ids.push(KEXSite.enqueue(() => true));
      let rejected = false; try { KEXSite.enqueue(() => true); } catch { rejected = true; }
      ids.forEach(KEXSite.cancel); return rejected;
    }));
    await page.goto(base + '/contact/');
    await page.waitForFunction(() => !document.querySelector('button[type=submit]').disabled);
    await page.click('button[type=submit]');
    assert.equal(await page.locator('#form-errors').isVisible(), true);
    assert.equal(await page.locator('.field-error').count(), 3);
    await page.fill('#name', 'Browser Fixture'); await page.fill('#email', 'fixture@example.invalid');
    await page.fill('#organisation', 'Fixture'); await page.fill('#message', 'Local DOM qualification only');
    await page.selectOption('#use_case', 'runtime-integration'); await page.check('#privacy_consent');
    assert.equal(await page.locator('#marketing_consent').isChecked(), false);
    let submissions = 0;
    await context.route(base + '/api/interest', async route => {
      submissions++;
      if (submissions === 1) {
        await delay(250);
        return route.fulfill({ status: 503, contentType: 'application/json', body: JSON.stringify({ error: 'Fixture temporary storage failure.' }) });
      }
      return route.continue();
    });
    await page.click('button[type=submit]');
    assert.equal(await page.locator('button[type=submit]').isDisabled(), true);
    await page.waitForFunction(() => !document.querySelector('button[type=submit]').disabled);
    assert.match(await page.locator('#form-errors').textContent(), /entries are retained/);
    assert.equal(await page.locator('#email').inputValue(), 'fixture@example.invalid');
    await page.click('button[type=submit]');
    await page.locator('#form-success').waitFor({ state: 'visible' });
    assert.match(await page.locator('#form-success').textContent(), /Your interest is recorded/);
    assert.match(await page.locator('#form-success').textContent(), /No email has been sent/);
    const degraded = await browser.newContext();
    await degraded.addInitScript(() => { window.fetch = undefined; window.Worker = undefined; window.BigInt = undefined; window.WebAssembly = undefined; });
    const basic = await degraded.newPage(); await basic.goto(base + '/contact/');
    assert.match(await basic.locator('#capture-status').textContent(), /unavailable/);
    assert.equal(await basic.locator('button[type=submit]').isDisabled(), true);
    await basic.goto(base + '/compatibility/'); assert.equal(await basic.locator('h1').count(), 1);
    const noJs = await browser.newContext({ javaScriptEnabled: false }); const plain = await noJs.newPage();
    await plain.goto(base + '/contact/'); assert.ok(await plain.locator('noscript').isVisible());
    assert.deepEqual(errors, []);
    console.log(JSON.stringify({ status: 'passed', ...counts, form: 'fixture persisted', wrapper: 'modes, queue limits, cooperative work and remote keys checked', degradedFeatures: 'fetch/Worker/BigInt/WebAssembly absent', hardware32BitVerified: false, nativePublicationVerified: false, chromiumSandbox: process.env.SITE_BROWSER_SANDBOX !== '0' }));
  } finally {
    if (browser) await browser.close();
    server.kill('SIGTERM'); await new Promise(resolve => server.once('exit', resolve));
    fs.rmSync(fixture, { recursive: true, force: true });
  }
})().catch(error => { console.error(error); process.exitCode = 1; });

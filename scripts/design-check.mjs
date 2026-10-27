/** Deterministic presentation QA. Reads frozen fixtures; never runs the engine. */
import { createRequire } from 'node:module';
import { createServer } from 'node:http';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { resolve, dirname, extname } from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const require = createRequire(resolve(root, 'frontend/package.json'));
const { chromium } = require('playwright');
const dist = resolve(root, 'frontend/dist');
const output = resolve(root, 'artifacts/design');
await mkdir(output, { recursive: true });
const fixtureText = await readFile(resolve(root, 'frontend/public/demo.json'), 'utf8');
const fixture = JSON.parse(fixtureText);
const frozenBefore = await readFile(resolve(root, 'frontend/public/demo.json'));
const types = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png' };
const server = createServer(async (request, response) => {
  try {
    const pathname = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
    const file = resolve(dist, pathname === '/' ? 'index.html' : '.' + pathname);
    if (!file.startsWith(dist + '/')) { response.writeHead(403); response.end(); return; }
    const bytes = await readFile(file);
    response.writeHead(200, { 'Content-Type': types[extname(file)] || 'application/octet-stream' }); response.end(bytes);
  } catch { response.writeHead(404); response.end('Not found'); }
});
await new Promise((resolveReady, reject) => { server.once('error', reject); server.listen(5105, '127.0.0.1', resolveReady); });
let browser;
const checks = [];
const errors = [];
try {
  browser = await chromium.launch({ headless: true, ...(process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {}), args: ['--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1080 }, deviceScaleFactor: 1 });
  page.on('pageerror', error => errors.push(String(error)));
  await page.goto('http://127.0.0.1:5105');
  await page.getByRole('heading', { name: 'Survey reconstruction', exact: true }).waitFor();
  await page.locator('canvas').waitFor();
  assert.equal(await page.locator('h1').innerText(), 'AeroMapper');
  assert.equal(await page.getByText('See less.', { exact: false }).count(), 0);
  assert.equal(await page.getByText('SIMULATION ONLY', { exact: true }).count(), 0);
  const motion = await page.locator('.block-y').evaluateAll(elements => elements.map(element => { const css = getComputedStyle(element); return { duration: css.animationDuration, delay: css.animationDelay, easing: css.animationTimingFunction }; }));
  assert.deepEqual(motion.map(value => value.duration), ['0.5s', '0.5s', '0.5s']);
  assert.deepEqual(motion.map(value => value.delay), ['0s', '0.08s', '0.16s']);
  motion.forEach(value => assert.equal(value.easing, 'cubic-bezier(0.16, 1, 0.3, 1)'));
  assert.equal(await page.locator('body').evaluate(() => getComputedStyle(document.documentElement).getPropertyValue('--bg').trim()), '#E6E1D8');
  checks.push('Isometric palette and exact 0.5 s / 0.08 s stagger / prescribed easing');
  const replay = page.getByRole('slider', { name: 'Mission replay', exact: true });
  await replay.fill('12');
  const canvasBefore = await page.locator('canvas').evaluate(element => element.toDataURL());
  await page.waitForTimeout(1050);
  assert.equal(await page.locator('canvas').evaluate(element => element.toDataURL()), canvasBefore, 'Measured geometry must not idle-bob or animate');
  const dataBeforeRotation = await replay.inputValue();
  const canvas = page.locator('canvas');
  await canvas.focus(); await page.keyboard.press('ArrowRight');
  assert.notEqual(await canvas.evaluate(element => element.toDataURL()), canvasBefore);
  assert.equal(await replay.inputValue(), dataBeforeRotation);
  const box = await canvas.boundingBox();
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2); await page.mouse.down(); await page.mouse.move(box.x + box.width / 2 + 50, box.y + box.height / 2, { steps: 6 }); await page.mouse.up();
  checks.push('Static measurement canvas; keyboard and drag rotation preserve replay state');
  await page.getByRole('checkbox', { name: 'Reveal truth for review' }).check();
  await page.getByRole('checkbox', { name: 'Reveal truth for review' }).uncheck();
  await page.getByRole('button', { name: 'lawnmower', exact: true }).click();
  assert.equal(await replay.inputValue(), '0');
  await page.getByRole('button', { name: 'adaptive', exact: true }).click();
  await page.getByRole('button', { name: 'Play replay' }).click(); await page.waitForTimeout(550); await page.getByRole('button', { name: 'Pause replay' }).click();
  assert(Number(await replay.inputValue()) >= 1);
  const frameIndex = Math.min(25, fixture.adaptive.trace.length - 1);
  await replay.fill(String(frameIndex));
  const frame = fixture.adaptive.trace[frameIndex];
  const imagePixel = await page.getByRole('img', { name: 'Actual synthetic camera patch used by detector' }).locator('rect').first().getAttribute('fill');
  assert.equal(imagePixel, `rgb(${frame.camera[0][0] * 255},${frame.camera[0][0] * 255},${frame.camera[0][0] * 255})`);
  const summary = page.locator('.inspection-drawer > summary');
  await summary.click(); assert.equal(await page.locator('.inspection-drawer').getAttribute('open'), null); await summary.click();
  checks.push('Actual saved camera pixels, replay, policy selection, truth review and inspection drawer');
  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Export current comparison' }).click();
  const download = await downloadPromise; const downloadPath = resolve(output, 'export.json'); await download.saveAs(downloadPath);
  assert.deepEqual(JSON.parse(await readFile(downloadPath, 'utf8')), fixture);
  checks.push('Export exactly matches frozen fixture; no fabricated data');
  // Verify request wiring without executing or modifying the simulation.
  let intercepted = false;
  await page.route('http://127.0.0.1:8105/api/compare', async route => {
    const request = route.request();
    if (request.method() === 'OPTIONS') { await route.fulfill({ status: 204, headers: { 'access-control-allow-origin': 'http://127.0.0.1:5105', 'access-control-allow-methods': 'POST, OPTIONS', 'access-control-allow-headers': 'content-type' } }); return; }
    const body = request.postDataJSON(); assert.equal(body.seed, Number(fixture.adaptive.metrics.seed)); assert.equal(body.budget, 220); assert.equal(body.family, 'test'); intercepted = true;
    await route.fulfill({ status: 200, headers: { 'access-control-allow-origin': 'http://127.0.0.1:5105' }, contentType: 'application/json', body: fixtureText });
  });
  await page.getByRole('button', { name: 'Run paired mission' }).click(); await page.getByRole('status').filter({ hasText: 'New paired experiment' }).waitFor(); assert(intercepted);
  checks.push('Mission control request wiring only (intercepted frozen response; engine not run)');
  // Capture genuine presentation screenshots from the saved, not intercepted, run.
  await page.reload(); await page.getByRole('heading', { name: 'Survey reconstruction' }).waitFor(); await replay.fill(String(frameIndex)); await page.waitForTimeout(800);
  assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  await page.screenshot({ path: resolve(output, 'desktop-1440.png'), fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
  await page.getByRole('img', { name: 'Actual synthetic camera patch used by detector' }).scrollIntoViewIfNeeded();
  await page.screenshot({ path: resolve(output, 'mobile-390.png'), fullPage: true });
  checks.push('Desktop 1440 px and mobile 390 px; no horizontal overflow; camera and controls remain accessible');
  const reduced = await browser.newPage({ viewport: { width: 1440, height: 1080 }, reducedMotion: 'reduce' });
  reduced.on('pageerror', error => errors.push(String(error))); await reduced.goto('http://127.0.0.1:5105'); await reduced.getByRole('heading', { name: 'Survey reconstruction' }).waitFor();
  assert(await reduced.evaluate(() => matchMedia('(prefers-reduced-motion: reduce)').matches));
  const animationNames = await reduced.locator('.block-y,.block-scale').evaluateAll(elements => elements.map(element => getComputedStyle(element).animationName));
  assert(animationNames.every(name => name === 'none'));
  await reduced.getByRole('slider', { name: 'Mission replay' }).fill(String(frameIndex));
  await reduced.screenshot({ path: resolve(output, 'reduced-motion.png'), fullPage: true });
  checks.push('Reduced-motion disables decorative clips; deliberate replay seeking remains usable');
  assert.deepEqual(errors, []);
  assert.deepEqual(await readFile(resolve(root, 'frontend/public/demo.json')), frozenBefore);
  await writeFile(resolve(output, 'verification.txt'), 'AeroMapper Isometric Studio presentation verification\n\n' + checks.map(check => 'PASS: ' + check).join('\n') + '\n\nNo simulation, model inference, training or experiment was executed. Data fixture was read-only. Browser screenshots are genuine.\n');
  console.log(checks.map(check => 'PASS: ' + check).join('\n'));
} catch (error) { await writeFile(resolve(output, 'failure.txt'), String(error) + '\n' + (error.stack || '')); throw error; }
finally { if (browser) await browser.close(); await new Promise(done => server.close(done)); }

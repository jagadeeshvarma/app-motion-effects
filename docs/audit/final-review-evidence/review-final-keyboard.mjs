/** Focus follow-up: native keyboard select input rather than selectOption. */
import { chromium } from '@playwright/test';
import { readFile, writeFile } from 'node:fs/promises';
import { createServer } from 'node:http';
import { join, extname } from 'node:path';
import { parseArgs } from 'node:util';
import { preflightStaticRoot, assertSafeStaticRequest } from '../../../evals/graders/safe-static-server.mjs';
const { values } = parseArgs({ options: { 'input-map': { type: 'string' }, 'output-file': { type: 'string' } } });
if (!values['input-map'] || !values['output-file']) throw Error('Require --input-map and --output-file');
const map = JSON.parse(await readFile(values['input-map'], 'utf8'));
const browser = await chromium.launch({ channel: 'chrome', headless: true });
const records = [];
for (const item of map.filter(x => ['J', 'L'].includes(x.scenario))) {
  const root = await preflightStaticRoot(join(item.source, item.app_root));
  const server = createServer(async (req, res) => {
    try {
      const file = await assertSafeStaticRequest(root, req.url);
      res.setHeader('Content-Type', { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css' }[extname(file)] || 'text/plain');
      res.end(await readFile(file));
    } catch { res.statusCode = 403; res.end('Unavailable'); }
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const origin = `http://127.0.0.1:${server.address().port}`;
  for (const width of [1280, 320]) {
    const context = await browser.newContext({ viewport: { width, height: 900 } });
    await context.route('**/*', route => route.request().url().startsWith(origin + '/') ? route.continue() : route.abort());
    const page = await context.newPage();
    await page.goto(origin);
    await page.locator('#filter').focus();
    const states = [];
    for (const key of ['r', 'a', 'r']) {
      await page.keyboard.press(key);
      await page.keyboard.press('Enter');
      states.push(await page.evaluate(() => ({ focus: document.activeElement.id, value: document.querySelector('#filter').value, feedback: document.querySelector('#feedback').textContent })));
    }
    records.push({ id: item.id, scenario: item.scenario, width, keys: ['r Enter', 'a Enter', 'r Enter'], states });
    await context.close();
  }
  await new Promise(resolve => server.close(resolve));
}
await browser.close();
await writeFile(values['output-file'], JSON.stringify(records, null, 2) + '\n');
console.log(JSON.stringify(records));

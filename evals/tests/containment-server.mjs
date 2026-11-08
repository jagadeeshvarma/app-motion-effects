/** Synthetic GA02 transport tests, no browser/model or external request. */
import assert from 'node:assert/strict';
import http from 'node:http';
import { mkdtemp, mkdir, writeFile, symlink, unlink, readFile, rm } from 'node:fs/promises';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { preflightStaticRoot, assertSafeStaticRequest, guardStaticHandler } from '../graders/safe-static-server.mjs';
const parent = await mkdtemp(join(tmpdir(), 'motion-ga02-http-'));
const root = join(parent, 'app');
let server;
try {
  await mkdir(root);
  await writeFile(join(root, 'index.html'), 'SYNTHETIC_INSIDE');
  await writeFile(join(parent, 'outside.txt'), 'SYNTHETIC_OUTSIDE_MUST_NOT_SERVE');
  const canonical = await preflightStaticRoot(root);
  assert.equal(await readFile(await assertSafeStaticRequest(canonical, '/'), 'utf8'), 'SYNTHETIC_INSIDE');
  await symlink(join(parent, 'outside.txt'), join(root, 'linked.txt'));
  await assert.rejects(preflightStaticRoot(root));
  await assert.rejects(assertSafeStaticRequest(canonical, '/linked.txt'));
  await symlink(parent, join(root, 'linked-directory'));
  await assert.rejects(assertSafeStaticRequest(canonical, '/linked-directory/outside.txt'));
  await mkdir(join(root, 'nested'));
  await symlink(join(parent, 'outside.txt'), join(root, 'nested/index.html'));
  await assert.rejects(assertSafeStaticRequest(canonical, '/nested/'));
  await assert.rejects(assertSafeStaticRequest(canonical, '/%2e%2e%2foutside.txt'));
  let unsafeListenerReached = false;
  server = http.createServer(guardStaticHandler(canonical, async (req, res) => {
    if (req.url === '/linked.txt') unsafeListenerReached = true;
    res.end(await readFile(join(root, req.url === '/' ? 'index.html' : req.url.slice(1))));
  }));
  await new Promise((resolve, reject) => { server.once('error', reject); server.listen(0, '127.0.0.1', resolve); });
  const get = (pathname) => new Promise((resolve, reject) => {
    http.get({hostname:'127.0.0.1', port:server.address().port, path:pathname}, response => {
      let body = ''; response.on('data', chunk => body += chunk); response.on('end', () => resolve({code:response.statusCode, body}));
    }).on('error', reject);
  });
  assert.deepEqual(await get('/'), {code:200, body:'SYNTHETIC_INSIDE'});
  const blocked = await get('/linked.txt');
  assert.equal(blocked.code, 403);
  assert.equal(unsafeListenerReached, false);
  assert.ok(!blocked.body.includes('SYNTHETIC_OUTSIDE'));
  await unlink(join(root, 'linked.txt'));
  await symlink(join(parent, 'does-not-exist'), join(root, 'broken'));
  await assert.rejects(assertSafeStaticRequest(canonical, '/broken'));
  console.log('GA02 static transport passed: same-origin symlink content never served.');
} finally {
  if (server) await new Promise(resolve => server.close(resolve));
  await rm(parent, {recursive:true, force:true});
}

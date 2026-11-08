/** Opt-in GA02 preload: preserve frozen grader source and replace transport only. */
import http from 'node:http';
import { syncBuiltinESMExports } from 'node:module';
import { guardStaticHandler, preflightStaticRoot } from './safe-static-server.mjs';

// Frozen web grader contract: node web.mjs SCENARIO APP_ROOT.
if (!process.argv[3]) throw new Error('GA02 requires the frozen web grader APP_ROOT argument');
const root = await preflightStaticRoot(process.argv[3]);
const createServer = http.createServer;
http.createServer = function guardedCreateServer(...args) {
  const index = args.length - 1;
  if (typeof args[index] !== 'function') throw new Error('GA02 requires a static request listener');
  args[index] = guardStaticHandler(root, args[index]);
  return createServer.apply(this, args);
};
// Frozen ESM imports of createServer receive the guarded builtin export.
syncBuiltinESMExports();

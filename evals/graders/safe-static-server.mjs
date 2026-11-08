/** GA02 transport guard. It does not change any frozen UI assertions. */
import { lstat, realpath, readdir } from 'node:fs/promises';
import { resolve, relative, isAbsolute, sep, join } from 'node:path';

function inside(root, candidate) {
  const local = relative(root, candidate);
  return local !== '..' && !local.startsWith('..' + sep) && !isAbsolute(local);
}

export async function preflightStaticRoot(appRoot) {
  const root = resolve(appRoot);
  const rootInfo = await lstat(root);
  if (rootInfo.isSymbolicLink() || !rootInfo.isDirectory()) throw new Error('Unsafe static root');
  async function visit(directory) {
    for (const name of await readdir(directory)) {
      const target = join(directory, name);
      const info = await lstat(target);
      if (info.isSymbolicLink() || (!info.isDirectory() && !info.isFile())) throw new Error('Unsafe submitted static entry');
      if (info.isDirectory()) await visit(target);
    }
  }
  await visit(root);
  return realpath(root);
}

export async function assertSafeStaticRequest(canonicalRoot, requestUrl) {
  const pathname = decodeURIComponent(new URL(requestUrl, 'http://localhost').pathname);
  if (pathname.includes('\0') || pathname.includes('\\')) throw new Error('Unsafe request path');
  let target = resolve(canonicalRoot, '.' + pathname);
  if (!inside(canonicalRoot, target)) throw new Error('Request leaves static root');
  async function components(candidate) {
    const local = relative(canonicalRoot, candidate);
    let current = canonicalRoot;
    const rootInfo = await lstat(current);
    if (rootInfo.isSymbolicLink() || !rootInfo.isDirectory()) throw new Error('Unsafe static root');
    for (const part of local.split(sep).filter(Boolean)) {
      current = join(current, part);
      const info = await lstat(current);
      if (info.isSymbolicLink() || (!info.isDirectory() && !info.isFile())) throw new Error('Unsafe static path component');
    }
    if (!inside(canonicalRoot, await realpath(candidate))) throw new Error('Resolved request leaves static root');
    return lstat(candidate);
  }
  let info = await components(target);
  if (info.isDirectory()) {
    target = join(target, 'index.html');
    info = await components(target);
  }
  if (!info.isFile()) throw new Error('Static target is not a regular file');
  return target;
}

export function guardStaticHandler(canonicalRoot, listener) {
  return async function guardedRequest(request, response) {
    try {
      await assertSafeStaticRequest(canonicalRoot, request.url);
    } catch {
      response.statusCode = 403;
      response.end('Not available');
      return;
    }
    return listener.call(this, request, response);
  };
}

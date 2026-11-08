#!/usr/bin/env node
import { createRequire } from 'node:module';
import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { resolve, extname, sep } from 'node:path';
import assert from 'node:assert/strict';
const require = createRequire(new URL('../../package.json', import.meta.url));
const { chromium } = require('@playwright/test');
const [id, appRoot] = process.argv.slice(2);
const root = resolve(appRoot);
const checks=[];
const check=async(name,fn)=>{try{await fn();checks.push({id:name,pass:true})}catch(error){checks.push({id:name,pass:false,detail:error.message})}};
const server=createServer(async(req,res)=>{try{let p=resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));if(p!==root&&!p.startsWith(root+sep))throw Error('outside root');if((await stat(p)).isDirectory())p=resolve(p,'index.html');const body=await readFile(p);res.setHeader('content-type',({'html':'text/html','js':'text/javascript','css':'text/css'})[extname(p).slice(1)]||'text/plain');res.end(body)}catch{res.statusCode=404;res.end('Not found')}});
let browser;
try{
 await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(0,'127.0.0.1',resolve)});
 const origin=`http://127.0.0.1:${server.address().port}`;
 browser=await chromium.launch({headless:true,channel:process.env.MOTION_BROWSER_CHANNEL||'chrome'});
 const context=await browser.newContext({viewport:{width:1000,height:760},reducedMotion:'no-preference'});
 const page=await context.newPage();page.setDefaultTimeout(1800);let external=[];let errors=[];
 await context.route('**/*',route=>{const url=route.request().url();if(!url.startsWith(origin+'/')&&!url.startsWith('data:')){external.push(url);return route.abort()}return route.continue()});
 page.on('pageerror',error=>errors.push(error.message));
 await page.goto(origin);await page.waitForTimeout(60);
 const visible=async(selector)=>page.locator(selector).isVisible();
 const text=selector=>page.locator(selector).textContent();
 const active=()=>page.evaluate(()=>document.getAnimations().some(a=>a.playState==='running'&&Number(a.effect?.getTiming().duration)>1));
 const noLongMotion=async()=>{await page.emulateMedia({reducedMotion:'reduce'});await page.waitForTimeout(30)};
 const noReducedAnimation=()=>page.evaluate(()=>document.getAnimations().every(a=>a.playState!=='running'||Number(a.effect?.getTiming().duration)<=1));
 const expectMotion=async(trigger)=>{await trigger();assert.ok(await active(),'No observable running state-change animation after trigger')};
 if(id==='A'){
  await check('save-pending-confirmed-persistence',async()=>{await page.fill('#draft','Pack spare labels');await page.click('#save');assert.equal(await page.evaluate(()=>window.__repoStats.successes),0);assert.ok(!/saved|success/i.test(await text('#feedback')),'Success shown before confirmation');await page.locator('#save').evaluate(b=>{b.click();b.click()});await page.waitForTimeout(420);assert.equal(await page.evaluate(()=>window.__repoStats.attempts),1);assert.equal(await page.evaluate(()=>window.__repoStats.successes),1);assert.match(await text('#notes'),/Pack spare labels/);await page.reload();assert.match(await text('#notes'),/Pack spare labels/)});
  await check('failure-draft-retry-motion',async()=>{await page.fill('#draft','Keep this draft');await page.check('#fail-next');await expectMotion(()=>page.click('#save'));await page.waitForTimeout(420);assert.equal(await page.inputValue('#draft'),'Keep this draft');assert.match(await text('#feedback'),/fail|error|try again/i);assert.doesNotMatch(await text('#notes'),/Keep this draft/);await page.uncheck('#fail-next');await page.click('#save');await page.waitForTimeout(420);assert.match(await text('#notes'),/Keep this draft/)});
  await check('reduced-motion-action',async()=>{await noLongMotion();await page.fill('#draft','Reduced motion note');await page.click('#save');assert.ok(await noReducedAnimation());await page.waitForTimeout(420);assert.match(await text('#notes'),/Reduced motion note/)});
 }
 if(id==='B'){
  await check('record-drafts-and-retargeting',async()=>{await page.fill('#draft','Lamp edited');await page.check('#priority');await expectMotion(()=>page.click('[data-record=two]'));assert.equal(await page.inputValue('#draft'),'Inspect the joint');await page.fill('#draft','Chair edited');await page.click('[data-record=one]');assert.equal(await page.inputValue('#draft'),'Lamp edited');assert.ok(await page.isChecked('#priority'));await page.click('[data-record=two]');assert.equal(await page.inputValue('#draft'),'Chair edited');assert.ok(await page.isChecked('#priority'));assert.equal(await page.locator('#draft').count(),1)});
  await check('keyboard-reduced-selection',async()=>{await noLongMotion();await page.focus('[data-record=one]');await page.keyboard.press('Enter');assert.equal(await text('#record-title'),'Lamp 12');assert.ok(await noReducedAnimation());await page.focus('#draft');await page.keyboard.press('End');await page.keyboard.type('!');assert.ok((await page.inputValue('#draft')).endsWith('!'))});
 }
 if(id==='E'){
  await check('dialog-keyboard-focus-escape',async()=>{await page.focus('#open');await page.keyboard.press('Enter');assert.ok(await visible('#editor'));const info=await page.locator('#editor').evaluate(el=>({role:el.getAttribute('role'),tag:el.tagName,label:el.getAttribute('aria-label'),labelledby:el.getAttribute('aria-labelledby')}));assert.ok(info.tag==='DIALOG'||info.role==='dialog','Missing dialog semantics');assert.ok(info.label||info.labelledby,'Missing accessible dialog name');assert.equal(await page.locator('#editor').evaluate(el=>el.contains(document.activeElement)),true);for(let n=0;n<6;n++){await page.keyboard.press('Tab');assert.ok(await page.locator('#editor').evaluate(el=>el.contains(document.activeElement)),'Tab escaped dialog')}await page.keyboard.press('Escape');await page.waitForTimeout(350);assert.ok(!(await visible('#editor')));assert.ok(await page.locator('#open').evaluate(el=>el===document.activeElement))});
  await check('dialog-motion-count-and-narrow-layout',async()=>{await expectMotion(()=>page.click('#open'));await page.fill('#count','9');await page.click('#confirm');await page.waitForTimeout(350);assert.match(await text('#feedback'),/9/);await page.setViewportSize({width:320,height:640});await page.click('#open');assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Horizontal overflow at 320px');await page.click('#cancel');await page.waitForTimeout(350)});
  await check('dialog-reduced-repeat',async()=>{await noLongMotion();for(let n=0;n<2;n++){await page.click('#open');assert.ok(await noReducedAnimation());await page.keyboard.press('Escape');await page.waitForTimeout(30);assert.ok(!(await visible('#editor')))}});
 }
 if(id==='F'){
  await check('authorization-feedback-and-draft',async()=>{for(const role of ['viewer','expired']){await page.selectOption('#permission',role);await page.fill('#address',`Draft for ${role}`);await page.click('#save');assert.ok(!/saved|success/i.test(await text('#feedback')),'Premature success');await page.waitForTimeout(400);assert.equal(await page.inputValue('#address'),`Draft for ${role}`);assert.match(await text('#feedback'),role==='viewer'?/permission|not allowed|cannot save|access/i:/expired|sign in|session/i);assert.equal(await page.evaluate(()=>window.__repoStats.successes),0);await page.waitForTimeout(700);assert.ok((await text('#feedback')).trim(),'Recovery message disappeared')}});
  await check('authorized-retry-duplicate-and-motion',async()=>{await page.selectOption('#permission','editor');const before=await page.evaluate(()=>window.__repoStats.attempts);await expectMotion(()=>page.click('#save'));await page.locator('#save').evaluate(b=>{b.click();b.click()});await page.waitForTimeout(400);assert.equal(await page.evaluate(()=>window.__repoStats.attempts),before+1);assert.equal(await page.evaluate(()=>window.__repoStats.successes),1);assert.match(await text('#feedback'),/saved|success|updated/i)});
  await check('reduced-feedback',async()=>{await noLongMotion();await page.click('#save');assert.ok(await noReducedAnimation())});
 }
 if(id==='G'){
  await check('text-boundary-with-motion',async()=>{const payload='<img src=x onerror="window.__injected=true"><script>window.__injected=true</script>';await page.fill('#message',payload);await expectMotion(()=>page.click('#preview'));assert.equal(await text('#message-content'),payload);await page.waitForTimeout(350);assert.equal(await page.evaluate(()=>Boolean(window.__injected)),false);assert.equal(await page.locator('#message-content img, #message-content script').count(),0);await page.click('#close');await page.waitForTimeout(350);assert.ok(!(await visible('#preview-panel')))});
  await check('interrupt-and-reduced-preview',async()=>{await page.click('#preview');await page.click('#close');await page.click('#preview');await page.waitForTimeout(350);assert.ok(await visible('#preview-panel'));await noLongMotion();await page.click('#close');await page.waitForTimeout(30);await page.click('#preview');assert.ok(await visible('#preview-panel'));assert.ok(await noReducedAnimation())});
 }
 if(id==='H'){
  await check('fast-colour-feedback',async()=>{const duration=await page.locator('#refresh').evaluate(el=>getComputedStyle(el).transitionDuration.split(',').map(s=>parseFloat(s)*(s.includes('ms')?1:1000)));assert.ok(duration.some(ms=>ms>=80&&ms<=200),'Refresh transition must be brief and perceptible');await page.click('#refresh');assert.equal(await text('#feedback'),'Queue refreshed')});
  await check('reduced-tiny-interaction',async()=>{await noLongMotion();await page.click('#refresh');assert.ok(await noReducedAnimation())});
 }
 if(id==='I'){
  await check('scoped-search-continuity',async()=>{await expectMotion(()=>page.fill('#search','A'));assert.equal(await page.locator('#shelves li:visible').count(),1);assert.equal(await page.locator('#search').evaluate(el=>el===document.activeElement),true);await page.fill('#search','missing');assert.equal(await page.locator('#shelves li:visible').count(),0);assert.match(await text('#feedback'),/0/);await page.fill('#search','B');await page.fill('#search','');assert.equal(await page.locator('#shelves li:visible').count(),2)});
  await check('search-reduced',async()=>{await noLongMotion();await page.fill('#search','A');assert.ok(await noReducedAnimation());assert.equal(await page.locator('#shelves li:visible').count(),1)});
 }
 if(id==='J'){
  await check('local-filter-motion',async()=>{await expectMotion(()=>page.selectOption('#filter','ready'));assert.equal(await page.locator('#kits li:visible').count(),1);assert.match(await text('#feedback'),/1/);await page.selectOption('#filter','all');assert.equal(await page.locator('#kits li:visible').count(),2)});
  await check('local-filter-reduced',async()=>{await noLongMotion();await page.selectOption('#filter','ready');assert.ok(await noReducedAnimation());assert.equal(await page.locator('#kits li:visible').count(),1)});
 }
 if(id==='K'){
  await check('handover-motion-and-interruption',async()=>{await page.fill('#handover','Do not reset my draft');await expectMotion(()=>page.click('#show'));await page.click('#hide');await page.click('#show');await page.waitForTimeout(350);assert.ok(await visible('#handover-panel'));assert.equal(await text('#handover-content'),'Do not reset my draft');assert.equal(await page.inputValue('#handover'),'Do not reset my draft')});
  await check('handover-reduced',async()=>{await noLongMotion();await page.click('#hide');await page.waitForTimeout(30);await page.click('#show');assert.ok(await noReducedAnimation());assert.ok(await visible('#handover-panel'))});
 }
 if(id==='L'){
  await check('repeat-single-handler-motion',async()=>{await expectMotion(()=>page.selectOption('#filter','ready'));assert.equal(await page.evaluate(()=>window.__filterStats.changes),1);assert.equal(await page.locator('#parcels li:visible').count(),1);await page.selectOption('#filter','all');assert.equal(await page.evaluate(()=>window.__filterStats.changes),2);assert.equal(await page.locator('#filter').count(),1);assert.equal(await page.locator('#parcels li:visible').count(),2)});
  await check('clean-reload-reduced',async()=>{await page.reload();assert.equal(await page.locator('#parcels li:visible').count(),2);await noLongMotion();await page.selectOption('#filter','ready');assert.ok(await noReducedAnimation());assert.equal(await page.evaluate(()=>window.__filterStats.changes),1)});
 }
 await check('no-browser-errors-or-external-transport',()=>{assert.deepEqual(errors,[]);assert.deepEqual(external,[])});
 await context.close();
 process.stdout.write(JSON.stringify({status:checks.every(c=>c.pass)?'pass':'fail',checks}));
}catch(error){process.stdout.write(JSON.stringify({status:'blocked',reason:error.message,checks}));process.exitCode=2}
finally{await browser?.close();await new Promise(resolve=>server.close(resolve))}

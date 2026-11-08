#!/usr/bin/env node
import { createRequire } from 'node:module';
import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { resolve, extname, sep } from 'node:path';
import assert from 'node:assert/strict';
const require = createRequire(new URL('../../../package.json', import.meta.url));
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
 const expectMotion=async(trigger)=>{await trigger();let observed=false;for(let n=0;n<14;n++){if(await active()){observed=true;break}await page.waitForTimeout(10)}assert.ok(observed,'No observable running state-change animation after trigger')};

 if(id==='M'){
  const order=()=>page.locator('#rounds > [data-task]').evaluateAll(rows=>rows.map(row=>row.dataset.task));
  await check('moved-row-continuity-and-state',async()=>{
   await page.fill('#note-valve','Keep this selected draft');await page.check('#done-valve');
   await page.locator('#note-valve').evaluate(el=>{el.setSelectionRange(2,8);window.__originalInput=el;window.__originalRow=el.closest('[data-task]')});
   await expectMotion(()=>page.click('#down-valve'));
   assert.ok(await page.locator('#row-valve').evaluate(el=>el.getAnimations({subtree:true}).some(a=>a.playState==='running'&&Number(a.effect?.getTiming().duration)>1)),'Moved row has no active continuity effect');
   assert.deepEqual(await order(),['pump','valve','meter']);
   assert.equal(await page.inputValue('#note-valve'),'Keep this selected draft');assert.ok(await page.isChecked('#done-valve'));
   assert.ok(await page.locator('#note-valve').evaluate(el=>el===window.__originalInput));assert.ok(await page.locator('#row-valve').evaluate(el=>el===window.__originalRow));
   assert.deepEqual(await page.locator('#note-valve').evaluate(el=>[el.selectionStart,el.selectionEnd]),[2,8]);
   assert.ok(await page.locator('#down-valve').evaluate(el=>el===document.activeElement),'Moved control lost focus');
  });
  await check('rapid-retargeting-and-order-contract',async()=>{
   await page.reload();await page.waitForTimeout(30);
   await page.evaluate(()=>{document.querySelector('#down-valve').click();document.querySelector('#up-valve').click();document.querySelector('#up-valve').click()});
   assert.deepEqual(await order(),['valve','pump','meter']);
   assert.equal(await page.evaluate(()=>window.__moveStats.moves),3);assert.ok(await page.isDisabled('#up-valve'));assert.ok(await page.isDisabled('#down-meter'));
   assert.equal(await page.locator('#rounds > [data-task]').count(),3);await page.reload();assert.deepEqual(await order(),['valve','pump','meter']);
  });
  await check('live-and-initial-reduced-motion',async()=>{
   await expectMotion(()=>page.click('#down-valve'));await page.emulateMedia({reducedMotion:'reduce'});await page.waitForTimeout(40);assert.ok(await noReducedAnimation(),'Live preference did not stop nonessential movement');
   await page.click('#up-valve');await page.waitForTimeout(40);assert.ok(await noReducedAnimation());assert.deepEqual(await order(),['valve','pump','meter']);
  });
 }
 if(id==='N'){
  const closed=async()=>{await page.waitForTimeout(400);assert.equal(await page.locator('#panel').evaluate(el=>el.open),false,'Dialog remained active after dismissal');assert.equal(await page.evaluate(()=>document.body.style.overflow),'','Background scroll lock leaked');assert.ok(await page.locator('#filters').evaluate(el=>el===document.activeElement),'Focus did not return to trigger')};
  await check('drawer-motion-filter-commit-and-focus',async()=>{
   await expectMotion(()=>page.click('#filters'));await page.waitForTimeout(260);
   assert.equal(await page.locator('#panel').evaluate(el=>el.contains(document.activeElement)),true);
   for(let n=0;n<5;n++){await page.keyboard.press('Tab');assert.ok(await page.locator('#panel').evaluate(el=>el.contains(document.activeElement)||document.activeElement===document.body),'Focus reached a background page control')}
   await page.check('#unpaid');await page.click('#apply');assert.equal(await page.locator('#receipts li').count(),9);await closed();
  });
  await check('no-transitionend-reduced-dismissal-and-draft',async()=>{
   await page.reload();await noLongMotion();await page.click('#filters');await page.waitForTimeout(40);await page.check('#unpaid');await page.click('#apply');await closed();assert.equal(await page.locator('#receipts li').count(),9);
   await page.click('#filters');await page.uncheck('#unpaid');await page.click('#cancel');await closed();assert.equal(await page.locator('#receipts li').count(),9);assert.match(await text('#feedback'),/Unpaid/);
   await page.click('#filters');assert.ok(await page.isChecked('#unpaid'));await page.keyboard.press('Escape');await closed();
  });
  await check('cancelled-exit-live-preference-scroll-and-reopen',async()=>{
   await page.emulateMedia({reducedMotion:'no-preference'});await page.reload();await page.evaluate(()=>window.scrollTo(0,250));const before=await page.evaluate(()=>scrollY);
   await page.click('#filters');await page.waitForTimeout(260);await page.click('#cancel');await page.emulateMedia({reducedMotion:'reduce'});await closed();
   assert.ok(Math.abs((await page.evaluate(()=>scrollY))-before)<=1,'Background scroll position changed');
   await page.click('#filters');await page.keyboard.press('Escape');await closed();
  });
  await check('forced-cancel-and-narrow-dialog',async()=>{
   await page.emulateMedia({reducedMotion:'no-preference'});await page.reload();await page.setViewportSize({width:320,height:640});await page.click('#filters');await page.waitForTimeout(260);
   assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
   await page.addStyleTag({content:'*,*::before,*::after{transition:none!important;animation:none!important}'});
   await page.click('#cancel');await closed();await page.click('#filters');await page.click('#apply');await closed();
  });
 }
 await check('no-browser-errors-or-external-transport',()=>{assert.deepEqual(errors,[]);assert.deepEqual(external,[])});
 await context.close();
 process.stdout.write(JSON.stringify({status:checks.every(c=>c.pass)?'pass':'fail',checks}));
}catch(error){process.stdout.write(JSON.stringify({status:'blocked',reason:error.message,checks}));process.exitCode=2}
finally{await browser?.close();await new Promise(resolve=>server.close(resolve))}

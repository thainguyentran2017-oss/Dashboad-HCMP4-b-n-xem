const {chromium}=require('playwright');
(async()=>{const f=process.argv[2];const b=await chromium.launch();const p=await b.newPage({viewport:{width:1400,height:900}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('file://'+process.cwd()+'/'+f);await p.waitForFunction(()=>typeof setTab==='function');await p.waitForTimeout(2500);
if(await p.isVisible('#vwGate')){await p.fill('#vwO','HCMP4');await p.click('#vwOk');await p.waitForTimeout(500);}
await p.locator('.tmbar .tmbtn').filter({hasText:'Chương trình'}).first().click();await p.waitForTimeout(300);await p.locator('#tab-club').click();await p.waitForTimeout(700);
const subs=await p.locator('.tmsub button').allInnerTexts();console.log(subs);const k=subs.findIndex(t=>/tiềm năng/.test(t));await p.locator('.tmsub button').nth(k).click();await p.waitForTimeout(1500);
console.log(await p.evaluate(()=>[$('hClP').textContent,$('lPF').innerText.replace(/\n/g,' '),($('lPTable').tBodies[0].rows[0]||{}).innerText,($('lPTable').tBodies[0].rows[5]||{}).innerText,$('lPNote').innerText].join('\n')));
await p.click('#lPF button[data-g="ws"]');await p.waitForTimeout(400);console.log('ws',await p.evaluate(()=>$('hClP').textContent));
await p.click('#lPF button[data-s="60/90"]');await p.waitForTimeout(400);console.log('60/90',await p.evaluate(()=>$('hClP').textContent));
await p.screenshot({path:'clp.png'});console.log('errs',errs);await b.close();})();

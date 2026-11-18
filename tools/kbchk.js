const {chromium}=require('playwright');
(async()=>{const f=process.argv[2], w=+process.argv[3]||1400;const b=await chromium.launch();const p=await b.newPage({viewport:{width:w,height:900}});
const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('file://'+process.cwd()+'/'+f);await p.waitForTimeout(3000);
const st=await p.evaluate(()=>{const g=[...document.querySelectorAll('.tmbtn')].find(b=>/Chương trình/.test(b.textContent));return g?'grp ok':'no grp'});
if(await p.isVisible('#vwGate')){await p.fill('#vwO','HCMP4');await p.click('#vwOk');await p.waitForTimeout(500);}
await p.locator('.tmbar .tmbtn').filter({hasText:'Chương trình'}).first().click();await p.waitForTimeout(300);await p.locator('#tab-kb').click();await p.waitForTimeout(700);
console.log('subs',await p.locator('.tmsub button').allInnerTexts());await p.locator('.tmsub button').first().click();await p.waitForTimeout(800);
const r=await p.evaluate(()=>({k:$('kbKpis').innerText.replace(/\n/g,' | '),sum:$('kbTable').innerText.split('\n').slice(0,9).join(' / '),
 L:$('hKbL').textContent, Lrows:$('kbLTable').tBodies[0].rows.length, N:$('hKbN').textContent, NF:$('kbNF').innerText.replace(/\n/g,' '), Nrow1:($('kbNTable').tBodies[0].rows[0]||{}).innerText,
 xls:[...document.querySelectorAll('#view-kb .xbtn')].filter(b=>b.offsetParent).length, inMenu:!!document.querySelector('#tab-kb'), aqf:!!document.querySelector('#tab-aqf')}));
console.log(st, JSON.stringify(r,null,1));
await p.click('#kbTable tbody tr.qrow');await p.waitForTimeout(400);
console.log('drill', await p.evaluate(()=>$('hKb').textContent+' rows '+$('kbTable').tBodies[0].rows.length+' back '+!$('kbBack').hidden+' L hidden '+$('kbLBox').hidden));
await p.click('#kbBack');await p.waitForTimeout(400);
console.log('back', await p.evaluate(()=>$('hKb').textContent+' '+$('kbBack').hidden));
await p.click('#kbNF button[data-s="g40"]');await p.waitForTimeout(300);
console.log('g40', await p.evaluate(()=>$('hKbN').textContent));
await p.selectOption('#kbNpp',{index:1});await p.waitForTimeout(300);
console.log('npp', await p.evaluate(()=>$('kbNpp').value+' | '+$('hKbL').textContent+' | '+$('hKbN').textContent));
await p.screenshot({path:'kb_'+w+'.png',fullPage:false});
console.log('errs',errs);await b.close();})();

// usage: node audit.js <file.html> <width>  — loads the page, visits every tab, reports page errors
const {chromium} = require('playwright');
(async () => {
  const [f, w] = [process.argv[2], +(process.argv[3] || 1400)];
  const b = await chromium.launch(), p = await b.newPage({viewport: {width: w, height: 900}}), er = [];
  p.on('pageerror', e => er.push(e.message));
  await p.goto('file://' + require('path').resolve(f)); await p.waitForTimeout(4000);
  const tabs = await p.evaluate(() => [...document.querySelectorAll('[role=tab][id^=tab-]')].map(t => t.id.slice(4)));
  for (const t of tabs){ await p.evaluate(t => { try { setTab(t); } catch(e){ throw e; } }, t).catch(e => er.push(t + ': ' + e.message)); await p.waitForTimeout(500); }
  const info = await p.evaluate(() => ({meta: (document.getElementById('meta') || {}).textContent, raw: (document.querySelector('.rawmiss') || {}).textContent}));
  console.log(f, w, 'tabs', tabs.length, JSON.stringify(info)); console.log(er.length ? 'ERRORS:\n' + er.join('\n') : 'no errors');
  await b.close();
})();

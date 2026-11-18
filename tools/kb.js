/* ---------- Trưng bày khối AQF (TBKhoiAQF_HCMP): DS ASO đăng ký (file DPM) · chỉ tiêu theo mức (Mức 5T = 20 thùng, Mức 10T = 40 thùng) · thực đạt = SL đi giao Aquafina chai nhựa (Rawdata) trong tháng, theo mã KH ---------- */
const KB = DATA.kaqf || {rows: [], m: '2026-11', code: ''};
const KB_K = new Set(DATA.skuNames.map((n, k) => /^Aquafina Chai nhựa/i.test(n) ? k : -1).filter(k => k >= 0));
let KB_BY = 'npp', KB_G = null, KB_ST = 'all', KBN_ST = 'all', KBN_N = 300;
function kbAct(m){ // KH → {q: AQF chai nhựa, q5: AQF 500ml, last}
  const o = new Map(), src = m === CUR_M ? CUR.skuEv : (PREV[m] || {}).skuEv;
  for (const [c, ri, di, k, q] of src || []){ if (!KB_K.has(k) || !(q > 0)) continue; let x = o.get(c); if (!x) o.set(c, x = {q: 0, q5: 0, last: 0}); x.q += q; if (A5_K.has(k)) x.q5 += q; x.last = Math.max(x.last, di + 1); }
  return {o, has: !!src};
}
function kbCtx(){
  const m = KB.m || CUR_M, npp = $('kbNpp').value, ss = $('kbSs').value, rt = $('kbRt').value, lv = $('kbLv').value, {o: act, has} = kbAct(m);
  const K = KB.rows.filter(x => { const r = R[x[1]]; return r && (!npp || r.npp === npp) && (!ss || r.ss === ss) && (!rt || r.code === rt) && (!lv || x[7] === lv); })
    .map(([c, ri, t, ok, dk, lh, seg, lv]) => { const a = act.get(c) || {q: 0, q5: 0, last: 0}, ef = (efOf(c) || [''])[0];
      return {c, ri, t, ok, dk, lh, seg, lv, a: a.q, a5: a.q5, last: a.last, done: t > 0 && a.q >= t - 1e-9, ef, efOk: ef === 'Hoàn thành ký'}; });
  return {m, has, K};
}
function kbAgg(L){ const o = {n: 0, ok: 0, t: 0, a: 0, done: 0, buy: 0, gap: 0, l5: 0, l10: 0};
  for (const x of L){ o.n++; if (x.ok) o.ok++; o.t += x.t; o.a += x.a; if (x.done) o.done++; else o.gap += x.t - x.a; if (x.a > 0) o.buy++; if (/5T/.test(x.lv)) o.l5++; else o.l10++; } return o; }
const KB_FL = {all: () => true, done: x => x.done, miss: x => !x.done, no: x => !x.a, l5: x => /5T/.test(x.lv), l10: x => /10T/.test(x.lv)};
function kbListHtml(X, L){
  const F = v => v ? fmt(Math.round(v)) : '', ML = 'T' + +X.m.slice(5), pill = (a, t) => { const p = ratio(a, t); return p == null ? '' : `<span class="aqp${p >= 1 ? ' ok' : p >= .5 ? ' mid' : ''}">${pctTxt(p)}</span>`; };
  const dl2 = d => d ? d.slice(8, 10) + '/' + d.slice(5, 7) : '', dl3 = n => n ? String(n).padStart(2, '0') + '/' + X.m.slice(5) : '';
  return `<thead><tr><th>STT</th><th>NPP</th><th>SS</th><th>Mã Route</th><th>Nhân viên</th><th>Mã KH</th><th>Tên KH</th><th>Thứ</th><th>Seg</th><th>Loại hình</th><th>Mức</th><th>Ngày<br>đăng ký</th><th>Trạng thái</th><th>Eframe</th><th class="hct">Chỉ tiêu<br>${ML}</th><th class="hac">Thực đạt AQF<br>${ML}</th><th>% đạt</th><th>Còn thiếu</th><th>Trong đó<br>AQF 500ml</th><th>Ngày mua<br>gần nhất</th></tr></thead><tbody>` +
    L.map((x, i) => { const ci = CI[x.c] || [], r = R[x.ri];
      return `<tr><td class="c">${i + 1}</td><td class="l">${esc(r.npp)}</td><td class="l">${esc(shortSs(r.ss))}</td><td>${r.code}</td><td class="l">${esc(r.dcr || '')}</td><td>${esc(CC[x.c])}</td><td class="l"><b>${esc(ci[0] || '')}</b></td><td class="c">${esc(thuTxt(ci[4]))}</td><td class="c">${esc(x.seg || ci[3] || '')}</td><td class="c">${esc(x.lh || lhOf(x.c))}</td><td class="c">${esc(x.lv)}</td><td class="c">${dl2(x.dk)}</td>` +
        `<td class="c">${x.ok ? '<span class="vst ok">Đã duyệt</span>' : '<span class="vst w">Chờ duyệt</span>'}</td><td class="c">${x.efOk ? '<span class="vst ok">Đã ký</span>' : `<span class="vst w">${esc(x.ef || 'Chưa có')}</span>`}</td><td class="num ct">${F(x.t)}</td><td class="num ac">${x.a ? fmt1(x.a) : (X.has ? '<b class="dn">0</b>' : '')}</td><td class="c">${X.has ? pill(x.a, x.t) : ''}</td><td class="num${x.done ? ' up' : ' dn'}">${x.done ? 'Đạt' : X.has ? fmt1(x.t - x.a) : ''}</td><td class="num">${x.a5 ? fmt1(x.a5) : ''}</td><td class="c">${dl3(x.last)}</td></tr>`; }).join('') +
    (L.length ? '' : '<tr><td colspan="20" class="c sub">Không có KH cho bộ lọc này.</td></tr>') + '</tbody>';
}
const kbKey = (by, x) => by === 'npp' ? R[x.ri].npp : by === 'ss' ? R[x.ri].ss : R[x.ri].code;
function kbRender(){
  if (!$('kbTable')) return;
  const rs0 = [...new Set(KB.rows.map(x => x[1]))].map(i => R[i]).filter(Boolean);
  if (!$('kbNpp').options.length){ opt($('kbNpp'), [['', 'Tất cả NPP'], ...[...new Set(rs0.map(r => r.npp))].sort().map(n => [n, n])]); opt($('kbLv'), [['', 'Tất cả mức'], ...[...new Set(KB.rows.map(x => x[7]))].sort((a, b) => parseFloat(a.replace(/\D+/g, '')) - parseFloat(b.replace(/\D+/g, ''))).map(v => [v, v])]); }
  { const npp = $('kbNpp').value, rs = rs0.filter(r => !npp || r.npp === npp);
    opt($('kbSs'), [['', 'Tất cả SS'], ...[...new Set(rs.map(r => r.ss))].sort().map(n => [n, shortSs(n)])], true);
    const ss = $('kbSs').value; opt($('kbRt'), [['', 'Tất cả tuyến'], ...rs.filter(r => !ss || r.ss === ss).sort((a, b) => a.code.localeCompare(b.code)).map(r => [r.code, r.code + ' · ' + (r.dcr || '')])], true); }
  const X = kbCtx(), T = kbAgg(X.K), F = v => v ? fmt(Math.round(v)) : '', ML = 'T' + +X.m.slice(5), last = DATES[DATES.length - 1];
  $('kbPace').innerHTML = `CT <b>${esc(KB.code)}</b> · ${ML}/${X.m.slice(0, 4)} · ${X.has ? (X.m === CUR_M ? `dữ liệu đến <b>${dLabel(last)}</b>` : 'đủ tháng') : '<b>chưa có dữ liệu tháng này</b>'}`;
  const tile = (t, v, d, c) => `<div class="ktile" style="--c:${c}"><div class="t">${t}</div><div class="v">${v}</div><div class="d">${d}</div></div>`;
  $('kbKpis').innerHTML = tile('KH đăng ký', fmt(T.n), `Đã duyệt <b>${fmt(T.ok)}</b>${T.n - T.ok ? ` · Chờ duyệt <b>${fmt(T.n - T.ok)}</b>` : ''}`, '#0284c7') +
    tile('Theo mức', `${fmt(T.l5)}<small> · ${fmt(T.l10)}</small>`, `Mức 5T <b>${fmt(T.l5)}</b> KH · Mức 10T <b>${fmt(T.l10)}</b> KH`, '#1f4e9c') +
    tile('Chỉ tiêu ' + ML, F(T.t) || '0', 'thùng AQF · Mức 5T 20 thùng, Mức 10T 40 thùng', '#c00000') +
    tile('Thực đạt ' + ML, X.has ? F(T.a) || '0' : '–', X.has ? `${pctTxt(ratio(T.a, T.t))} chỉ tiêu · còn thiếu <b>${F(T.gap) || 0}</b> thùng` : 'chưa có Rawdata', '#15803d') +
    tile('KH đạt chỉ tiêu', X.has ? fmt(T.done) : '–', `${pctTxt(ratio(T.done, T.n))} KH đăng ký · có mua <b>${fmt(T.buy)}</b> · chưa mua <b class="dn">${fmt(T.n - T.buy)}</b>`, '#7c3aed');
  $('kbNote').innerHTML = `${esc(KB.name || 'Trưng bày khối AQF')} · DS đăng ký từ file DPM (${fmt(KB.rows.length)} KH) · Chỉ tiêu theo file: Mức 5T = 20 thùng, Mức 10T = 40 thùng · Thực đạt = SL đi giao <b>Aquafina chai nhựa</b> (500ml, 355ml, 1,5L, 5L) ${ML} từ Rawdata, cột riêng AQF 500ml · Bấm vào dòng để xem danh sách KH`;
  $('kbBy').querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', b.dataset.by === KB_BY));
  $('kbBy').hidden = !!KB_G; $('kbBack').hidden = !KB_G;
  const T0 = $('kbTable');
  if (KB_G){ $('kbLBox').hidden = true; $('kbNBox').hidden = true;
    const [by, key] = KB_G, all = X.K.filter(x => kbKey(by, x) === key);
    const btn = (k, t) => `<button type="button" class="tqb" data-s="${k}" aria-pressed="${KB_ST === k}">${t} <b>${fmt(all.filter(KB_FL[k]).length)}</b></button>`;
    $('kbF').innerHTML = btn('all', 'Tất cả') + btn('done', '✓ Đạt chỉ tiêu') + btn('miss', 'Chưa đạt') + btn('no', '✕ Chưa mua') + btn('l5', 'Mức 5T') + btn('l10', 'Mức 10T');
    const L = all.filter(KB_FL[KB_ST]).sort((a, b) => R[a.ri].code.localeCompare(R[b.ri].code) || thuK(a.c) - thuK(b.c) || (a.a - a.t) - (b.a - b.t));
    $('hKb').textContent = `${by === 'rt' ? key + ' · ' + ((R.find(r => r.code === key) || {}).dcr || '') : by === 'ss' ? shortSs(key) : key} · ${fmt(all.length)} KH`;
    T0.innerHTML = kbListHtml(X, L); return;
  }
  $('kbLBox').hidden = false; $('kbNBox').hidden = false; kbListRender(X); kbNRender();
  $('kbF').innerHTML = ''; $('hKb').textContent = 'Tracking Trưng bày khối AQF';
  const G = new Map(); for (const x of X.K){ const k = kbKey(KB_BY, x); if (!G.has(k)) G.set(k, []); G.get(k).push(x); }
  const keys = [...G.keys()].sort((a, b) => String(a).localeCompare(String(b)));
  const lab = k => KB_BY === 'rt' ? `<td class="l"><b>${k}</b></td><td class="l">${esc((R.find(r => r.code === k) || {}).dcr || '')}</td>` : `<td class="l" colspan="2"><b>${esc(KB_BY === 'ss' ? shortSs(k) : k)}</b></td>`;
  const pill = (a, t) => { const p = ratio(a, t); return p == null ? '' : `<span class="aqp${p >= 1 ? ' ok' : p >= .5 ? ' mid' : ''}">${pctTxt(p)}</span>`; };
  const row = (l, L, k) => { const a = kbAgg(L); return `<tr${k != null ? ` class="qrow" data-k="${esc(k)}" title="Bấm để xem danh sách KH"` : ''}>${l}<td class="num">${fmt(a.n)}</td><td class="num">${a.l5 ? fmt(a.l5) : ''}</td><td class="num">${a.l10 ? fmt(a.l10) : ''}</td><td class="num ct">${F(a.t)}</td><td class="num ac">${X.has ? F(a.a) : ''}</td><td class="c">${X.has ? pill(a.a, a.t) : ''}</td><td class="num up">${a.done ? fmt(a.done) : ''}</td><td class="num dn">${a.n - a.done ? fmt(a.n - a.done) : ''}</td><td class="num dn">${a.n - a.buy ? fmt(a.n - a.buy) : ''}</td><td class="num dn">${F(a.gap)}</td></tr>`; };
  T0.innerHTML = `<thead><tr><th colspan="2">${KB_BY === 'npp' ? 'NPP' : KB_BY === 'ss' ? 'SS' : 'Tuyến · Nhân viên'}</th><th>KH đăng ký</th><th>Mức 5T</th><th>Mức 10T</th><th class="hct">Chỉ tiêu<br>${ML}</th><th class="hac">Thực đạt AQF<br>${ML}</th><th>% đạt</th><th>KH đạt</th><th>KH chưa đạt</th><th>KH chưa mua</th><th>Còn thiếu<br>(thùng)</th></tr></thead><tbody>` +
    keys.map(k => row(lab(k), G.get(k), k)).join('') + `</tbody><tfoot>${row('<td class="l" colspan="2">Tổng</td>', X.K)}</tfoot>`;
}
function kbListRender(X){
  X = X || kbCtx(); const q = ($('kbQ').value || '').trim().toLowerCase();
  const all = X.K.filter(x => !q || [CC[x.c], (CI[x.c] || [])[0], R[x.ri].code, R[x.ri].dcr].some(v => String(v || '').toLowerCase().includes(q)));
  const btn = (k, t) => `<button type="button" class="tqb" data-s="${k}" aria-pressed="${KB_ST === k}">${t} <b>${fmt(all.filter(KB_FL[k]).length)}</b></button>`;
  $('kbLF').innerHTML = btn('all', 'Tất cả') + btn('done', '✓ Đạt chỉ tiêu') + btn('miss', 'Chưa đạt') + btn('no', '✕ Chưa mua') + btn('l5', 'Mức 5T') + btn('l10', 'Mức 10T');
  const L = all.filter(KB_FL[KB_ST]).sort((a, b) => { const A = R[a.ri], B = R[b.ri]; return A.npp.localeCompare(B.npp) || shortSs(A.ss).localeCompare(shortSs(B.ss), 'vi') || A.code.localeCompare(B.code) || thuK(a.c) - thuK(b.c); });
  $('hKbL').textContent = `Danh sách khách hàng tham gia · ${fmt(L.length)} KH`;
  $('kbLTable').innerHTML = kbListHtml(X, L);
}
const KBN_LH = /^(WS[A-Z0-9]*|TH|CHTL|MM)$/; // cùng nhóm loại hình đang tham gia CT (TH, CHTL, WS)
const KBN_FL = {all: () => true, g40: x => x.a >= 40 - 1e-9, g20: x => x.a >= 20 - 1e-9 && x.a < 40 - 1e-9, lt: x => x.a < 20 - 1e-9};
function kbNRender(){ // KH có lấy AQF trong tháng, không có trong DS Tích luỹ AQF 500ml và chưa đăng ký Trưng bày khối AQF
  const m = KB.m || CUR_M, npp = $('kbNpp').value, ss = $('kbSs').value, rt = $('kbRt').value, q = ($('kbNQ').value || '').trim().toLowerCase(), ML = 'T' + +m.slice(5);
  const {o: act, has} = kbAct(m), reg = new Set([...A5.rows.map(x => x[0]), ...KB.rows.map(x => x[0])]), own = new Map(), lastRi = new Map(), src = m === CUR_M ? CUR.skuEv : (PREV[m] || {}).skuEv;
  for (const i of R.keys()) for (const c of R[i].kh || []) if (!own.has(c)) own.set(c, i);
  for (const [c, ri, di, k, qq] of src || []) if (KB_K.has(k) && qq > 0) lastRi.set(c, ri);
  const all = [];
  for (const [c, a] of act){ if (reg.has(c) || !KBN_LH.test(String((CI[c] || [])[2] || '').toUpperCase())) continue;
    const ri = own.has(c) ? own.get(c) : lastRi.get(c), r = R[ri]; if (!r || (npp && r.npp !== npp) || (ss && r.ss !== ss) || (rt && r.code !== rt)) continue;
    if (q && ![CC[c], (CI[c] || [])[0], r.code, r.dcr].some(v => String(v || '').toLowerCase().includes(q))) continue;
    all.push({c, ri, a: a.q, a5: a.q5, last: a.last}); }
  const btn = (k, t) => `<button type="button" class="tqb" data-s="${k}" aria-pressed="${KBN_ST === k}">${t} <b>${fmt(all.filter(KBN_FL[k]).length)}</b></button>`;
  $('kbNF').innerHTML = btn('all', 'Tất cả') + btn('g40', '≥ 40 thùng (đủ Mức 10T)') + btn('g20', '20 – dưới 40 thùng (đủ Mức 5T)') + btn('lt', 'Dưới 20 thùng');
  const L = all.filter(KBN_FL[KBN_ST]).sort((x, y) => y.a - x.a || R[x.ri].code.localeCompare(R[y.ri].code)), tot = L.reduce((s, x) => s + x.a, 0);
  $('hKbN').textContent = `KH không tham gia Tích luỹ AQF 500ml và chưa đăng ký Trưng bày khối AQF · ${fmt(L.length)} KH`;
  $('kbNNote').innerHTML = has ? `KH có lấy Aquafina chai nhựa ${ML} (${dLabel(m + '-01').slice(0, 5)} – ${m === CUR_M ? dLabel(DATES[DATES.length - 1]) : 'cuối tháng'}) · loại hình TH, CHTL, MM, WS · không có trong DS Tích luỹ AQF 500ml và DS Trưng bày khối AQF trên DPM · xếp theo SL giảm dần · tổng <b>${fmt1(tot)}</b> thùng` : `${ML} chưa có Rawdata`;
  const dl3 = n => n ? String(n).padStart(2, '0') + '/' + m.slice(5) : '';
  $('kbNTable').innerHTML = `<thead><tr><th>STT</th><th>NPP</th><th>SS</th><th>Mã Route</th><th>Nhân viên</th><th>Mã KH</th><th>Tên KH</th><th>Thứ</th><th>Seg</th><th>Loại hình</th><th class="hac">SL AQF<br>${ML} (thùng)</th><th>Trong đó<br>AQF 500ml</th><th>Đủ SL mức</th><th>Ngày mua<br>gần nhất</th></tr></thead><tbody>` +
    L.slice(0, KBN_N).map((x, i) => { const ci = CI[x.c] || [], r = R[x.ri], lv = x.a >= 40 - 1e-9 ? '<span class="vst ok">Mức 10T</span>' : x.a >= 20 - 1e-9 ? '<span class="vst ok">Mức 5T</span>' : '';
      return `<tr><td class="c">${i + 1}</td><td class="l">${esc(r.npp)}</td><td class="l">${esc(shortSs(r.ss))}</td><td>${r.code}</td><td class="l">${esc(r.dcr || '')}</td><td>${esc(CC[x.c])}</td><td class="l"><b>${esc(ci[0] || '')}</b></td><td class="c">${esc(thuTxt(ci[4]))}</td><td class="c">${esc(ci[3] || '')}</td><td class="c">${esc(lhOf(x.c))}</td><td class="num ac">${fmt1(x.a)}</td><td class="num">${x.a5 ? fmt1(x.a5) : ''}</td><td class="c">${lv}</td><td class="c">${dl3(x.last)}</td></tr>`; }).join('') +
    (L.length ? '' : '<tr><td colspan="14" class="c sub">Không có KH cho bộ lọc này.</td></tr>') + '</tbody>';
  $('kbNMore').hidden = L.length <= KBN_N; $('kbNMore').textContent = `Xem thêm (${fmt(L.length - KBN_N)})`;
}
$('tab-kb').addEventListener('click', () => setTab('kb'));
$('kbBy').addEventListener('click', e => { const b = e.target.closest('button[data-by]'); if (!b) return; KB_BY = b.dataset.by; kbRender(); });
$('kbTable').addEventListener('click', e => { const tr = e.target.closest('tr.qrow'); if (!tr || KB_G) return; KB_G = [KB_BY, tr.dataset.k]; KB_ST = 'all'; kbRender(); $('hKb').scrollIntoView({block: 'nearest'}); });
$('kbBack').addEventListener('click', () => { const k = KB_G && KB_G[1]; KB_G = null; KB_ST = 'all'; kbRender(); const tr = [...$('kbTable').querySelectorAll('tr.qrow')].find(t => t.dataset.k === k); if (tr){ tr.scrollIntoView({block: 'center'}); tr.classList.add('krflash'); setTimeout(() => tr.classList.remove('krflash'), 1600); } });
$('kbF').addEventListener('click', e => { const b = e.target.closest('button[data-s]'); if (!b) return; KB_ST = b.dataset.s; kbRender(); });
$('kbLF').addEventListener('click', e => { const b = e.target.closest('button[data-s]'); if (!b) return; KB_ST = b.dataset.s; kbListRender(); });
$('kbNF').addEventListener('click', e => { const b = e.target.closest('button[data-s]'); if (!b) return; KBN_ST = b.dataset.s; KBN_N = 300; kbNRender(); });
$('kbNMore').addEventListener('click', () => { KBN_N += 500; kbNRender(); });
$('kbQ').addEventListener('input', () => kbListRender());
$('kbNQ').addEventListener('input', () => { KBN_N = 300; kbNRender(); });
['kbNpp', 'kbSs', 'kbRt', 'kbLv'].forEach(id => $(id).addEventListener('change', () => { if (id === 'kbNpp'){ $('kbSs').value = ''; $('kbRt').value = ''; } if (id === 'kbSs') $('kbRt').value = ''; KB_G = null; KBN_N = 300; kbRender(); }));
$('kbReset').addEventListener('click', () => { ['kbNpp', 'kbSs', 'kbRt', 'kbLv', 'kbQ', 'kbNQ'].forEach(id => $(id).value = ''); KB_G = null; KB_ST = 'all'; KBN_ST = 'all'; KBN_N = 300; kbRender(); });
$('kbXls').addEventListener('click', () => tableXls($('kbTable'), 'TRƯNG BÀY KHỐI AQF · ' + $('hKb').textContent, $('kbNote').textContent, `Trung_bay_khoi_AQF_tong_hop.xlsx`, $('kbMsg')));
$('kbLXls').addEventListener('click', () => tableXls($('kbLTable'), 'TRƯNG BÀY KHỐI AQF · ' + $('hKbL').textContent, $('kbNote').textContent, `DS_KH_Trung_bay_khoi_AQF.xlsx`, $('kbLMsg')));
$('kbNXls').addEventListener('click', async () => { const n = KBN_N; KBN_N = 1e9; kbNRender(); try { await tableXls($('kbNTable'), 'TRƯNG BÀY KHỐI AQF · ' + $('hKbN').textContent, $('kbNNote').textContent, `KH_chua_DK_Trung_bay_khoi_AQF.xlsx`, $('kbNMsg')); } finally { KBN_N = n; kbNRender(); } });

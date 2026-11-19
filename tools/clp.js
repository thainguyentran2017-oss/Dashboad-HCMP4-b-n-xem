/* ---------- Club: KH tiềm năng ký Club — chưa có trong DS Club và DS VIP Tết của tháng, sản lượng tháng trước (đủ tháng) hoặc dự kiến tháng này đạt mức Club thấp nhất (LRB−AQF ≥ 20, LRB ≥ 30) ---------- */
const CLP_TIER = [[60, 90], [40, 65], [30, 50], [20, 30]]; // Mức 1 LRB−AQF / Mức 2 LRB
let CLP_ST = 'all', CLP_G = '', CLP_N = 300;
const clpTier = (n1, l) => CLP_TIER.find(([a, b]) => n1 >= a - 1e-9 && l >= b - 1e-9) || null;
const clpGrp = lh => /^WS/.test(lh) ? 'ws' : /^(TH|CHTL|MM)$/.test(lh) ? 'rt' : 'afh';
function clPList(X){
  const m = X.m, pm = mShift(m, 1), reg = new Set([...(CLUB[m] || []).map(x => x[0]), ...(TITAN[m] || []).map(x => x[0])]);
  const VF = ctVol(m, 1, 31), VP = PREV[pm] || pm === CUR_M ? ctVol(pm, 1, 31) : new Map(), nd = m === CUR_M ? +DATES[DATES.length - 1].slice(8, 10) : dim(m), f = dim(m) / Math.max(1, nd);
  const own = new Map(); for (const i of R.keys()) for (const c of R[i].kh || []) if (!own.has(c)) own.set(c, i);
  const L = [];
  for (const c of new Set([...VF.keys(), ...VP.keys()])){
    if (reg.has(c)) continue; const ri = own.get(c); if (ri == null || !X.RS.has(ri)) continue;
    const p = VP.get(c) || {L: 0, A: 0}, v = VF.get(c) || {L: 0, A: 0}, p1 = p.L - p.A, v1 = v.L - v.A, e1 = v1 * f, eL = v.L * f;
    const tp = clpTier(p1, p.L), te = clpTier(e1, eL); if (!tp && !te) continue;
    const t = !tp ? te : !te ? tp : (tp[1] >= te[1] ? tp : te), lh = String((CI[c] || [])[2] || '').toUpperCase();
    L.push({c, ri, lh, g: clpGrp(lh), pL: p.L, p1, vL: v.L, v1, eL, e1, t, by: tp && te ? 'both' : tp ? 'p' : 'e'});
  }
  return {L, m, pm, nd, hasP: !!(PREV[pm] && PREV[pm].skuEv)};
}
function clPRender(X){
  if (!$('lPTable')) return; X = X || clCtx();
  const P = clPList(X), q = ($('lPQ').value || '').trim().toLowerCase(), ML = 'T' + +P.m.slice(5), PL = 'T' + +P.pm.slice(5);
  const base = P.L.filter(x => (!CLP_G || x.g === CLP_G) && (!q || [CC[x.c], (CI[x.c] || [])[0], R[x.ri].code, R[x.ri].dcr].some(v => String(v || '').toLowerCase().includes(q))));
  const tk = x => x.t[0] + '/' + x.t[1], btn = (k, t, n) => `<button type="button" data-s="${k}" aria-pressed="${CLP_ST === k}">${t} <b>${fmt(n)}</b></button>`;
  const gb = (k, t) => `<button type="button" data-g="${k}" aria-pressed="${CLP_G === k}">${t} <b>${fmt(P.L.filter(x => !k || x.g === k).length)}</b></button>`;
  $('lPF').innerHTML = '<span class="lab">Nhóm</span>' + gb('', 'Tất cả') + gb('rt', 'TH · CHTL · MM') + gb('ws', 'WS') + gb('afh', 'AFH / khác') +
    '<span class="lab" style="margin-left:10px">Mức gợi ý</span>' + btn('all', 'Tất cả', base.length) + CLP_TIER.map(([a, b]) => btn(a + '/' + b, `${a}/${b}`, base.filter(x => tk(x) === a + '/' + b).length)).join('');
  const L = base.filter(x => CLP_ST === 'all' || tk(x) === CLP_ST).sort((a, b) => b.t[1] - a.t[1] || Math.max(b.pL, b.eL) - Math.max(a.pL, a.eL));
  $('hClP').textContent = `KH tiềm năng ký Club · chưa ký Club & VIP Tết ${ML} · ${fmt(L.length)} KH`;
  $('lPNote').innerHTML = `Không có trong DS Club và DS VIP Tết ${ML} · đạt mức Club thấp nhất (LRB−AQF ≥ 20 &amp; LRB ≥ 30 thùng) theo sản lượng <b>${PL} đủ tháng</b>${P.hasP ? '' : ' (chưa có dữ liệu)'} hoặc <b>${ML} dự kiến</b> (đi giao 01–${String(P.nd).padStart(2, '0')}/${P.m.slice(5)} quy ra ${dim(P.m)} ngày) · Mức gợi ý (LRB−AQF / LRB) = mức cao nhất KH đạt được · theo bộ lọc NPP / SS / DCR / Nhóm phía trên`;
  const F = v => v ? fmt1(v) : '', BY = {both: `${PL} & ${ML}`, p: PL + ' đủ tháng', e: ML + ' dự kiến'};
  $('lPTable').innerHTML = `<thead><tr><th rowspan="2">STT</th><th rowspan="2">NPP</th><th rowspan="2">SS</th><th rowspan="2">Mã Route</th><th rowspan="2">Nhân viên</th><th rowspan="2">Mã KH</th><th rowspan="2">Tên KH</th><th rowspan="2">Thứ</th><th rowspan="2">Seg</th><th rowspan="2">Loại hình</th><th colspan="2">${PL} (đủ tháng)</th><th colspan="2">${ML} đến ${String(P.nd).padStart(2, '0')}/${P.m.slice(5)}</th><th colspan="2" class="hac">${ML} dự kiến</th><th rowspan="2" class="hct">Mức gợi ý<br>LRB−AQF / LRB</th><th rowspan="2">Căn cứ</th></tr>` +
    `<tr><th>LRB−AQF</th><th>LRB</th><th>LRB−AQF</th><th>LRB</th><th class="hac">LRB−AQF</th><th class="hac">LRB</th></tr></thead><tbody>` +
    L.slice(0, CLP_N).map((x, i) => { const ci = CI[x.c] || [], r = R[x.ri];
      return `<tr><td class="c">${i + 1}</td><td class="l">${esc(r.npp)}</td><td class="l">${esc(shortSs(r.ss))}</td><td>${r.code}</td><td class="l">${esc(r.dcr || '')}</td><td>${esc(CC[x.c])}</td><td class="l"><b>${esc(ci[0] || '')}</b></td><td class="c">${esc(thuTxt(ci[4]))}</td><td class="c">${esc(ci[3] || '')}</td><td class="c">${esc(lhOf(x.c))}</td>` +
        `<td class="num">${F(x.p1)}</td><td class="num">${F(x.pL)}</td><td class="num">${F(x.v1)}</td><td class="num">${F(x.vL)}</td><td class="num ac">${F(x.e1)}</td><td class="num ac">${F(x.eL)}</td><td class="c"><span class="vst ok">${x.t[0]} / ${x.t[1]}</span></td><td class="c">${BY[x.by]}</td></tr>`; }).join('') +
    (L.length ? '' : '<tr><td colspan="18" class="c sub">Không có KH cho bộ lọc này.</td></tr>') + '</tbody>';
  $('lPMore').hidden = L.length <= CLP_N; $('lPMore').textContent = `Xem thêm (${fmt(L.length - CLP_N)})`;
}
$('lPF').addEventListener('click', e => { const b = e.target.closest('button'); if (!b) return; if (b.dataset.g != null) CLP_G = b.dataset.g; if (b.dataset.s != null) CLP_ST = b.dataset.s; CLP_N = 300; clPRender(); });
$('lPMore').addEventListener('click', () => { CLP_N += 500; clPRender(); });
$('lPQ').addEventListener('input', () => { CLP_N = 300; clPRender(); });
$('lPXls').addEventListener('click', async () => { const n = CLP_N; CLP_N = 1e9; clPRender(); try { await tableXls($('lPTable'), 'CLUB · ' + $('hClP').textContent, $('lPNote').textContent, `KH_tiem_nang_Club_${$('lMonth').value}.xlsx`, $('lPMsg')); } finally { CLP_N = n; clPRender(); } });

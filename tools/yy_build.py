# So sánh 2025–2026 NPP Bình Hồng (chỉ bản chính): DATA.yy từ DATA.prev (data/p*.js) + tháng hiện tại
import json, glob, os, collections, datetime, calendar, sys
P = '/home/claude/sdo-de.html'; NPP = 'BINH HONG'
SRC = ['/home/claude/data', '/home/claude/dashboad-hcmp4-b-n-xem/data']
s = open(P, encoding='utf8').read(); i = s.index('const DATA = ') + 13; j = s.index(';</script>', i); D = json.loads(s[i:j])
import re, unicodedata
# sản phẩm = nhãn + vị/dòng + loại bao bì + dung tích; bỏ phần chỉ là tên mùa/khuyến mãi/quy cách (Tết, Mới, KM, Tray, Khay, Lốc 6, x24/x28…)
def pkey(n):
  t = unicodedata.normalize('NFC', n).lower().replace('–', '-')
  m = re.search(r'^(.*?)\s*(lon|can|chai nhựa|chai thủy tinh|chai)\s*(\d{3,4})', t)
  if not m: return None, n
  pre, pack, ml = m.group(1), m.group(2), m.group(3)
  pre = re.sub(r'\b(nước tăng lực|hương vị|regular)\b', ' ', pre); pre = re.sub(r'\btrà\b', ' ', pre); pre = re.sub(r'\btea\+\s*', 'tea+ ', pre)
  pre = re.sub(r'\b(oolong|ô long|olong)\b', 'ô long', pre); pre = re.sub(r'\bcoffee\b', 'coffee', pre); pre = re.sub(r'\s+', ' ', pre).strip()
  if pre.startswith('ô long'): pre = 'tea+ ' + pre
  pre = re.sub(r'^7up\b', '7up', pre)
  pk = {'lon': 'Lon', 'chai nhựa': 'Chai nhựa', 'chai thủy tinh': 'Chai thủy tinh', 'chai': 'Chai nhựa', 'can': 'Lon'}[pack]
  disp = ' '.join(w.capitalize() if not re.match(r'^(tea\+|7up|boss)$', w) else {'tea+': 'Tea+', '7up': '7UP', 'boss': 'BOSS'}[w] for w in pre.split())
  return f'{pre}|{pk}|{ml}', f'{disp} {pk} {ml}ml'
PKD = {}
R = D['routes']; BH = {k for k, r in enumerate(R) if r['npp'] == NPP}; G = D['skuGrp']; SB = D['skuBrand']
PK = []
for k, n in enumerate(D['skuNames']):
  key, disp = pkey(n); key = key or 'g' + str(G[k]); PK.append(key); PKD.setdefault(key, disp)
def loadp(m):
  for d in SRC:
    f = f'{d}/p{m}.js'
    if os.path.exists(f):
      t = open(f, encoding='utf8').read(); k = t.index('=') + 1; return json.loads(t[k:].rstrip().rstrip(';'))
CUR = D['dates'][-1][:7]
months = [f'{y}-{m:02d}' for y in (2025, 2026) for m in range(1, 13)]
sund = lambda y, m, upto=None: sum(1 for d in range(1, (upto or calendar.monthrange(y, m)[1]) + 1) if datetime.date(y, m, d).weekday() != 6)
out = {}
for m in months:
  if m > CUR: continue
  ev = D['skuEv'] if m == CUR else ((loadp(m) or {}).get('skuEv'))
  if not ev: continue
  rows = [x for x in ev if x[1] in BH]
  if not rows: continue
  q = 0; qb = collections.Counter(); ks = collections.defaultdict(set); visit = set(); lines = 0; pq = collections.Counter(); pk = collections.defaultdict(set); days = set()
  for c, ri, di, sk, v in rows:
    q += v; qb[SB[sk][0]] += v; g = G[sk]; ks[c].add(g); visit.add((c, di)); lines += 1; pq[PK[sk]] += v; pk[PK[sk]].add(c); days.add(di)
  o = {'q': round(q, 1), 'b': {str(b): round(v, 1) for b, v in qb.items()}, 'aso': len(ks), 'sku': sum(len(v) for v in ks.values()), 'ord': len(visit), 'ln': lines,
       'p': {str(g): [round(pq[g], 1), len(pk[g])] for g in pq}, 'pc': {str(g): sorted(pk[g]) for g in pk}}
  o['p'] = {str(g): v for g, v in o['p'].items()}
  # bao phủ theo nhãn: số KH mua nhãn trong tháng
  bk = collections.defaultdict(set)
  for c, ri, di, sk, v in rows:
    if v > 0: bk[SB[sk][0]].add(c)
  o['bk'] = {str(b): len(v) for b, v in bk.items()}
  # cùng kỳ năm trước của tháng đang chạy (cắt đến cùng ngày) để so "đến hiện tại"
  if m == str(int(CUR[:4]) - 1) + CUR[4:]:
    last = int(D['dates'][-1][8:]); cq = collections.Counter(); ck = collections.defaultdict(set); ca = set(); ct = 0
    for c, ri, di, sk, v in rows:
      if di + 1 > last: continue
      ct += v; cq[SB[sk][0]] += v; ca.add(c)
      if v > 0: ck[SB[sk][0]].add(c)
    o['cut'] = {'d': last, 'q': round(ct, 1), 'aso': len(ca), 'b': {str(b): round(v, 1) for b, v in cq.items()}, 'bk': {str(b): len(v) for b, v in ck.items()}}
  if m == CUR:
    y, mo = int(m[:4]), int(m[5:]); last = int(D['dates'][-1][8:]); o['mtd'] = last; o['wd'] = sund(y, mo, last); o['wdt'] = sund(y, mo)
  out[m] = o
# sản phẩm mới: nhóm SKU có bán năm 2026 nhưng không bán trong các tháng 2025 đã có dữ liệu
g25 = set(); g26 = set()
for m, o in out.items(): (g25 if m < '2026' else g26).update(o['p'])
NEW = sorted(g26 - g25, key=lambda g: -sum(out[m]['p'].get(g, [0])[0] for m in out if m >= '2026'))
nm = dict(PKD); BRK = {}
for k, n in enumerate(D['skuNames']): BRK.setdefault(PK[k], SB[k][0])
U26 = collections.defaultdict(set)
for m, o in out.items():
  pc = o.pop('pc'); kh = set()
  for g in NEW: kh.update(pc.get(g, []))
  if m >= '2026':
    for g in NEW: U26[g].update(pc.get(g, []))
    U26['*'].update(x for v in pc.values() for x in v); U26['+'].update(kh)
  o['nk'] = len(kh); o['nbp'] = round(len(kh) / o['aso'] * 100, 1) if o['aso'] else 0; o['nq'] = round(sum(o['p'].get(g, [0])[0] for g in NEW), 1)
  o['p'] = {g: v for g, v in o['p'].items() if g in NEW}
TG = {m: round(sum(v[10] for c, v in K.items() if c in {R[x]['code'] for x in BH}), 1) for m, K in (D.get('kpi') or {}).items()}
D['yy'] = {'npp': NPP, 'tg': TG, 'cur': CUR, 'm': out, 'new': [[g, nm[g], BRK[g], len(U26[g])] for g in NEW], 'u26': [len(U26['*']), len(U26['+'])], 'y25': sorted(m for m in out if m < '2026')}
s = s[:i] + json.dumps(D, ensure_ascii=False, separators=(',', ':')) + s[j:]; open(P, 'w', encoding='utf8').write(s)
print({m: (o['q'], o['aso'], o.get('mtd')) for m, o in out.items()}); print('SP mới', len(NEW), [nm[g] for g in NEW[:12]])

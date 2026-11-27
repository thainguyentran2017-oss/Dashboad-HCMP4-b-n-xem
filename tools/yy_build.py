# So sánh 2025–2026 NPP Bình Hồng (chỉ bản chính): DATA.yy từ DATA.prev (data/p*.js) + tháng hiện tại
import json, glob, os, collections, datetime, calendar, sys
P = '/home/claude/sdo-de.html'; NPP = 'BINH HONG'
SRC = [os.path.join(os.path.dirname(os.path.abspath(__file__)), 'artifact-files/5be14cf6-68f9-490e-b618-32570abc5ec6/data'), '/home/claude/dashboad-hcmp4-b-n-xem/data']
s = open(P, encoding='utf8').read(); i = s.index('const DATA = ') + 13; j = s.index(';</script>', i); D = json.loads(s[i:j])
R = D['routes']; BH = {k for k, r in enumerate(R) if r['npp'] == NPP}; G = D['skuGrp']; SB = D['skuBrand']
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
    q += v; qb[SB[sk][0]] += v; g = G[sk]; ks[c].add(g); visit.add((c, di)); lines += 1; pq[g] += v; pk[g].add(c); days.add(di)
  o = {'q': round(q, 1), 'b': {str(b): round(v, 1) for b, v in qb.items()}, 'aso': len(ks), 'sku': sum(len(v) for v in ks.values()), 'ord': len(visit), 'ln': lines,
       'p': {str(g): [round(pq[g], 1), len(pk[g])] for g in pq}, 'pc': {str(g): sorted(pk[g]) for g in pk}}
  if m == CUR:
    y, mo = int(m[:4]), int(m[5:]); last = int(D['dates'][-1][8:]); o['mtd'] = last; o['wd'] = sund(y, mo, last); o['wdt'] = sund(y, mo)
  out[m] = o
# sản phẩm mới: nhóm SKU có bán năm 2026 nhưng không bán trong các tháng 2025 đã có dữ liệu
g25 = set(); g26 = set()
for m, o in out.items(): (g25 if m < '2026' else g26).update(o['p'])
NEW = sorted(g26 - g25, key=lambda g: -sum(out[m]['p'].get(g, [0])[0] for m in out if m >= '2026'))
nm = {}
for k, n in enumerate(D['skuNames']):
  g = str(G[k]); nm[g] = n if g not in nm or len(n) < len(nm[g]) else nm[g]
for m, o in out.items():
  pc = o.pop('pc'); kh = set()
  for g in NEW: kh.update(pc.get(g, []))
  o['nk'] = len(kh); o['nq'] = round(sum(o['p'].get(g, [0])[0] for g in NEW), 1)
  o['p'] = {g: v for g, v in o['p'].items() if g in NEW}
TG = {m: round(sum(v[10] for c, v in K.items() if c in {R[x]['code'] for x in BH}), 1) for m, K in (D.get('kpi') or {}).items()}
D['yy'] = {'npp': NPP, 'tg': TG, 'cur': CUR, 'm': out, 'new': [[g, nm[g], SB[D['skuNames'].index(nm[g])][0]] for g in NEW], 'y25': sorted(m for m in out if m < '2026')}
s = s[:i] + json.dumps(D, ensure_ascii=False, separators=(',', ':')) + s[j:]; open(P, 'w', encoding='utf8').write(s)
print({m: (o['q'], o['aso'], o.get('mtd')) for m, o in out.items()}); print('SP mới', len(NEW), [nm[g] for g in NEW[:12]])

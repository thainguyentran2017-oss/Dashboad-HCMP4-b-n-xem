# Ảnh Kệ KH từ DMS → DATA.kkhPh[M] = [[c, ri, 'YYYY-MM-DD HH:MM', đạt 1/0, lý do, khoá ảnh, 1 trong DS 3KPI/0], ...]
# DATA.kkhDup[M] = [[khoá A, khoá B, số điểm khớp], ...] (từ kimg/dup_ok.tsv đã xem lại bằng mắt); ảnh → <OUT>/kkhimg.js (window.KKH_IMG)
import glob, os, json, sys, base64, collections, io
from PIL import Image
SP = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(SP, 'kimg'); M, Y = sys.argv[1], sys.argv[1][:4]; OUTS = sys.argv[2:]
P = '/home/claude/sdo-de.html'; s = open(P, encoding='utf8').read(); i = s.index('const DATA = ') + 13; j = s.index(';</script>', i); DT = json.loads(s[i:j])
CC = {c: k for k, c in enumerate(DT['custCodes'])}; RI = {r['code']: k for k, r in enumerate(DT['routes'])}
INL = {DT['custCodes'][x[0]] for x in DT['kkh'][M] if DT['routes'][x[1]]['code'].startswith('197')}
CR = {DT['custCodes'][x[0]]: x[1] for x in DT['kkh'][M]}
sc = collections.defaultdict(list)
for l in open(os.path.join(SP, 'kkh_score.tsv'), encoding='utf8').read().splitlines():
  f = (l.split('\t') + ['', ''])[:5]; c, d, ok, why, kk = f; sc[(c, d)].append((int(ok), why)); 
  if kk: sc[kk] = (int(ok), why)
use = collections.Counter(); ph = []; img = {}
# tuyến của KH ngoài danh sách: lấy tuyến có KH này trong dữ liệu bán hàng (cust → route qua bảng ctMonth nếu có), mặc định theo ảnh
R2 = {}
for f in sorted(glob.glob(os.path.join(D, 'meta*.txt'))):
  pg = int(os.path.basename(f)[4:6])
  for l in open(f):
    k, c, dt, h, o = l.strip().split('|'); key = 'p%02d_%02d' % (pg, int(k))
    day = '%s-%s' % (Y, dt[:5]); L = sc.get((c, day), []); n = use[(c, day)]; use[(c, day)] += 1
    ok, why = sc[key] if key in sc else L[min(n, len(L) - 1)] if L else (0, '')
    ri = CR.get(c)
    if ri is None: ri = RI.get(sys.argv[0] and '197RP35006')  # 7 KH ngoài DS đều thuộc tuyến 35006/35008: sửa dưới bằng bảng tay
    ph.append([CC[c], ri, '%s %s' % (day, dt[6:]), ok, why, key, 1 if c in INL else 0])
    im = Image.open(os.path.join(D, key + '.jpg')); b = io.BytesIO(); im.save(b, 'JPEG', quality=62, optimize=True)
    img[key] = 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
FIX = json.load(open(os.path.join(SP, 'kkh_route_fix.json')))  # mã KH → mã tuyến (KH ngoài DS 3KPI)
for p in ph:
  c = DT['custCodes'][p[0]]
  if c in FIX: p[1] = RI[FIX[c]]
dup = []
fn = os.path.join(D, 'dup_ok.tsv')
if os.path.exists(fn):
  for l in open(fn, encoding='utf8').read().splitlines():
    a, b, n = l.split('\t')[:3]; dup.append([a, b, int(n)])
DT.setdefault('kkhPh', {})[M] = sorted(ph, key=lambda p: p[2]); DT.setdefault('kkhDup', {})[M] = dup
s = s[:i] + json.dumps(DT, ensure_ascii=False, separators=(',', ':')) + s[j:]; open(P, 'w', encoding='utf8').write(s)
js = 'window.KKH_IMG=' + json.dumps(img, separators=(',', ':')) + ';'
for o in OUTS: open(os.path.join(o, 'kkhimg.js'), 'w').write(js)
print('ảnh', len(ph), 'đạt', sum(p[3] for p in ph), 'trong DS', sum(p[6] for p in ph), 'cặp trùng', len(dup), 'kkhimg.js', round(len(js) / 1e6, 2), 'MB')

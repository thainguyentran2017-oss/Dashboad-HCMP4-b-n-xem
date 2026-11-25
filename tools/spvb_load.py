# Báo cáo kết quả 3KPI: sheet "Công cụ trưng bày SPVB" → DATA.spvb[M] = [[c, ri, loại(0 tủ,1 CVS,2 Tea,3 AQF), QR, loại CH]]
#                       sheet "CCTB Kệ Khách hàng"    → DATA.kkh[M]  = [[c, ri, số lần đạt, đạt(0/1), mức]]
import openpyxl, json, sys, collections
SRC, M = sys.argv[1], sys.argv[2]; APPLY = 'apply' in sys.argv; P = '/home/claude/sdo-de.html'
s = open(P, encoding='utf8').read(); i = s.index('const DATA = '); j = s.index(';</script>', i); D = json.loads(s[i+13:j])
CC = {c: k for k, c in enumerate(D['custCodes'])}; RI = {r['code']: k for k, r in enumerate(D['routes'])}
wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
st = lambda v: '' if v is None else str(v).strip()
TY = {'VC': 0, 'CVS': 1, 'RGB': 1, 'KETRA': 2, 'AQF': 3}
bad = collections.Counter(); newc = 0
def cid(kh, name):
  global newc
  if kh not in CC: CC[kh] = len(D['custCodes']); D['custCodes'].append(kh); D['custInfo'].append([name, '', '', '', '']); newc += 1
  return CC[kh]
A = []
for r in list(wb['Công cụ trưng bày SPVB'].iter_rows(min_row=6, values_only=True)):
  kh = st(r[9]).upper()
  if not kh.startswith('CT'): continue
  ri = RI.get(st(r[6])); t = TY.get(st(r[17]))
  if ri is None or t is None: bad[(st(r[6]), st(r[17]))] += 1; continue
  A.append([cid(kh, st(r[10])), ri, t, st(r[19]), st(r[14])])
K = []
for r in list(wb['CCTB Kệ Khách hàng'].iter_rows(min_row=6, values_only=True)):
  kh = st(r[11]).upper()
  if not kh.startswith('CT'): continue
  ri = RI.get(st(r[10]))
  if ri is None: bad[(st(r[10]), 'KeKH')] += 1; continue
  K.append([cid(kh, ''), ri, int(float(st(r[12]) or 0)), 1 if st(r[13]) == 'Đạt' else 0, st(r[7])])
print('SPVB', len(A), collections.Counter(t for *_, t, q, l in [(x[0], x[1], x[2], x[3], x[4]) for x in A]) if False else collections.Counter(x[2] for x in A), 'Kệ KH', len(K), 'bad', dict(bad), 'new codes', newc)
print('SPVB theo NPP', collections.Counter(D['routes'][x[1]]['npp'] for x in A)); print('Kệ KH theo NPP', collections.Counter(D['routes'][x[1]]['npp'] for x in K))
if APPLY:
  D.setdefault('spvb', {})[M] = A; D.setdefault('kkh', {})[M] = K
  s = s[:i] + 'const DATA = ' + json.dumps(D, ensure_ascii=False, separators=(',', ':')) + s[j:]; open(P, 'w', encoding='utf8').write(s); print('applied')

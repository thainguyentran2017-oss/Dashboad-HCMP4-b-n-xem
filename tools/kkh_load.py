# Báo cáo 3KPI sheet "CCTB Khách hàng" (Kệ KH, có kết quả từng tuần) → cập nhật DATA.kkh[M] cho các KH trong file: [c, ri, số lần đạt, đạt(0/1), mức, [kq tuần 1..5: 1 đạt / 0 rớt / null chưa chấm], [lý do tuần]]
import openpyxl, json, sys, collections
SRC, M = sys.argv[1], sys.argv[2]; P = '/home/claude/sdo-de.html'
s = open(P, encoding='utf8').read(); i = s.index('const DATA = ') + 13; j = s.index(';</script>', i); D = json.loads(s[i:j])
CC = {c: k for k, c in enumerate(D['custCodes'])}; RI = {r['code']: k for k, r in enumerate(D['routes'])}
ws = openpyxl.load_workbook(SRC, read_only=True, data_only=True).worksheets[0]; R = list(ws.iter_rows(values_only=True)); H = [str(x or '') for x in R[4]]
st = lambda v: '' if v is None else str(v).strip()
ix = lambda name: H.index(name)
REA = ['Không chụp ảnh', 'Hình ASO Đóng cửa', 'Không chụp ảnh CCTB', '_Non-Compliance', 'Ảnh không chuẩn', 'Chưa Đạt Vị trí', 'Trưng bày còn SP đối thủ', 'TB Không đầy ngăn']
new = {}
for r in R[5:]:
  kh = st(r[ix('Ma KH')]).upper()
  if not kh.startswith('CT'): continue
  c, ri = CC.get(kh), RI.get(st(r[ix('Ma SalesRoute')]))
  if c is None or ri is None: print('skip', kh); continue
  wk, why = [], []
  for w in range(1, 6):
    kq = st(r[ix('Kết quả Trưng bày Tuần %d' % w)])
    wk.append(1 if kq == 'Đạt' else 0 if kq == 'Rớt' else None)
    rs = [nm.replace('_', '').strip() for nm in REA for h in H if h.startswith('Tuần %d' % w) and nm in h and st(r[H.index(h)]) == '1']
    why.append(', '.join(dict.fromkeys(rs)) or st(r[ix('Tuần %d - Lý do Không đạt' % w)]))
  new[c] = [c, ri, int(float(st(r[ix('Số lần đạt TB/ tháng')]) or 0)), 1 if st(r[ix('KQ Đạt TB tháng')]) == 'Đạt' else 0, st(r[ix('Muc Chuong Trinh')]), wk, why]
old = D.setdefault('kkh', {}).get(M, []); keep = [x for x in old if x[0] not in new]
D['kkh'][M] = keep + list(new.values())
print('file KH', len(new), 'NPP', collections.Counter(D['routes'][x[1]]['npp'] for x in new.values()), 'old', len(old), 'now', len(D['kkh'][M]))
print('tuần đã chấm', [sum(1 for x in new.values() if x[5][w] is not None) for w in range(5)], 'đạt', [sum(1 for x in new.values() if x[5][w] == 1) for w in range(5)], 'lý do T1', collections.Counter(x[6][0] for x in new.values()))
s = s[:i] + json.dumps(D, ensure_ascii=False, separators=(',', ':')) + s[j:]; open(P, 'w', encoding='utf8').write(s)

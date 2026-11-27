# File Tracking CT Loyalty (xlsb, sheet "Danh sách chi tiết") → DATA.loy[cidx] = [tổng chỉ tiêu, thực hiện LRB−AQF, tiền thưởng, số tháng đạt] lũy kế T1..T(M)
# cột tháng: chỉ tiêu 110+, SL LRB−Aqua suối 122+, Kết quả 134+, Tiền thưởng 158+ (tháng 1 = +0)
from python_calamine import CalamineWorkbook; import sys, json
SRC, M = sys.argv[1], int(sys.argv[2]); P = '/home/claude/sdo-de.html'
R = CalamineWorkbook.from_path(SRC).get_sheet_by_name('Danh sách chi tiết').to_python(skip_empty_area=False)
h = R[5]; assert str(h[110]).startswith('Tháng 1') and str(h[158]).startswith('Tháng 1'), h[110]
s = open(P, encoding='utf8').read(); i = s.index('const DATA = ') + 13; j = s.index(';</script>', i); D = json.loads(s[i:j])
CC = {c: k for k, c in enumerate(D['custCodes'])}; num = lambda v: float(v) if isinstance(v, (int, float)) else 0.0
L = dict(D.get('loy', {})); n = 0; miss = 0
for r in R[7:]:
  kh = str(r[8]).strip().upper()
  if not kh.startswith('CT'): continue
  if kh not in CC: miss += 1; continue
  t = sum(num(r[110 + m]) for m in range(M)); a = sum(num(r[122 + m]) for m in range(M)); mo = sum(num(r[158 + m]) for m in range(M)); k = sum(1 for m in range(M) if str(r[134 + m]).strip() == 'Đạt')
  if t or a or mo: L[str(CC[kh])] = [round(t, 1), round(a, 1), round(mo), k]; n += 1
D['loy'] = L
s = s[:i] + json.dumps(D, ensure_ascii=False, separators=(',', ':')) + s[j:]
s = s.replace("LOY_TO = '2026-09'", "LOY_TO = '2026-%02d'" % M) if "LOY_TO = '2026-09'" in s else s
open(P, 'w', encoding='utf8').write(s); print('loy KH', n, 'not in DMS', miss, 'total keys', len(L))

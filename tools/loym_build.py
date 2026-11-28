# Loyalty (file Tracking CT Loyalty, sheet "Danh sách chi tiết") → DATA.loyM: theo tháng, NPP Bình Hồng: KH tham gia / đạt / chỉ tiêu / SL LRB−Aqua suối của Club, Titan, Vip Tết và tổng ASO
from python_calamine import CalamineWorkbook; import sys, json, re
SRC, ASOF = sys.argv[1], sys.argv[2]; P = '/home/claude/sdo-de.html'; NPP = 'BINH HONG'
R = CalamineWorkbook.from_path(SRC).get_sheet_by_name('Danh sách chi tiết').to_python(skip_empty_area=False)
h = R[5]; assert str(h[37]).startswith('Tháng 1') and str(h[73]).startswith('Tháng 1'), h[37]
num = lambda v: float(v) if isinstance(v, (int, float)) else 0.0
grp = lambda p: 'vt' if p.startswith('Vip') else 'ti' if p.startswith('Titan') else 'cl' if p.startswith('Silver') or p.startswith('Club') else None
s0 = open(P, encoding='utf8').read(); i0 = s0.index('const DATA = ') + 13; j0 = s0.index(';</script>', i0); D0 = json.loads(s0[i0:j0])
RI = {r['code']: k for k, r in enumerate(D0['routes'])}; TL = []; rows = []; MX = 0
for r in R[7:]:
  if str(r[4]).strip() != NPP or not str(r[8]).strip().upper().startswith('CT'): continue
  ri = RI.get(str(r[6]).strip(), -1); P_ = ''; K = ''; T = []; A = []; LV = []
  for mi in range(12):
    p = str(r[37 + mi]).strip(); g = grp(p)
    P_ += {'cl': 'c', 'ti': 't', 'vt': 'v'}.get(g, '-'); K += '1' if g and str(r[73 + mi]).strip() == 'Đạt' else '0'
    T.append(round(num(r[49 + mi]), 1) if g else 0); A.append(round(num(r[61 + mi]), 1) if g else 0)
    if g and p not in TL: TL.append(p)
    LV.append(TL.index(p) if g else -1)
    if g: MX = max(MX, mi + 1)
  if P_.strip('-'): rows.append([ri, str(r[8]).strip().upper(), P_, K, T, A, LV])
print('KH', len(rows), 'không khớp tuyến', sum(1 for x in rows if x[0] < 0), 'tháng', MX)
s = open(P, encoding='utf8').read(); i = s.index('const DATA = ') + 13; j = s.index(';</script>', i); D = json.loads(s[i:j])
D['loyM'] = {'npp': NPP, 'asof': ASOF, 'mx': MX, 'tl': TL, 'rows': rows}
s = s[:i] + json.dumps(D, ensure_ascii=False, separators=(',', ':')) + s[j:]; open(P, 'w', encoding='utf8').write(s)


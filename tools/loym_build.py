# Loyalty (file Tracking CT Loyalty, sheet "Danh sách chi tiết") → DATA.loyM: theo tháng, NPP Bình Hồng: KH tham gia / đạt / chỉ tiêu / SL LRB−Aqua suối của Club, Titan, Vip Tết và tổng ASO
from python_calamine import CalamineWorkbook; import sys, json, re
SRC, ASOF = sys.argv[1], sys.argv[2]; P = '/home/claude/sdo-de.html'; NPP = 'BINH HONG'
R = CalamineWorkbook.from_path(SRC).get_sheet_by_name('Danh sách chi tiết').to_python(skip_empty_area=False)
h = R[5]; assert str(h[37]).startswith('Tháng 1') and str(h[73]).startswith('Tháng 1'), h[37]
num = lambda v: float(v) if isinstance(v, (int, float)) else 0.0
grp = lambda p: 'vt' if p.startswith('Vip') else 'ti' if p.startswith('Titan') else 'cl' if p.startswith('Silver') or p.startswith('Club') else None
M = {}
for mi in range(12):
  o = {g: {'n': 0, 'ok': 0, 't': 0.0, 'a': 0.0, 'lv': {}} for g in ('cl', 'ti', 'vt', 'all')}; any_ = False
  for r in R[7:]:
    if str(r[4]).strip() != NPP or not str(r[8]).strip().upper().startswith('CT'): continue
    p = str(r[37 + mi]).strip(); g = grp(p)
    if not g: continue
    any_ = True; ok = str(r[73 + mi]).strip() == 'Đạt'; t = num(r[49 + mi]); a = num(r[61 + mi])
    for k in (g, 'all'):
      x = o[k]; x['n'] += 1; x['ok'] += ok; x['t'] += t; x['a'] += a
    o[g]['lv'][p] = o[g]['lv'].get(p, 0) + 1
  if any_:
    for x in o.values(): x['t'] = round(x['t'], 1); x['a'] = round(x['a'], 1)
    M[str(mi + 1)] = o
s = open(P, encoding='utf8').read(); i = s.index('const DATA = ') + 13; j = s.index(';</script>', i); D = json.loads(s[i:j])
D['loyM'] = {'npp': NPP, 'asof': ASOF, 'm': M}
s = s[:i] + json.dumps(D, ensure_ascii=False, separators=(',', ':')) + s[j:]; open(P, 'w', encoding='utf8').write(s)
for k, o in M.items(): print(k, {g: (x['n'], x['ok'], round(x['a'])) for g, x in o.items()})

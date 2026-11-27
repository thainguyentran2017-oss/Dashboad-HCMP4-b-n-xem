# Chấm ảnh Kệ KH từ DMS (kkh_score.tsv: mã KH, ngày, 1 đạt/0 rớt, lý do) → DATA.kkh[M] cho các KH Bình Hồng trong danh sách 3KPI
import json, sys, collections
SC, M, TODAY = sys.argv[1], sys.argv[2], int(sys.argv[3]); P = '/home/claude/sdo-de.html'
s = open(P, encoding='utf8').read(); i = s.index('const DATA = ') + 13; j = s.index(';</script>', i); D = json.loads(s[i:j])
cc = D['custCodes']; R = D['routes']
wkOf = lambda d: 0 if d <= 8 else 1 if d <= 15 else 2 if d <= 22 else 3 if d <= 29 else 4
WEND = [8, 15, 22, 29, 31]
S = collections.defaultdict(list)
for l in open(SC, encoding='utf8').read().splitlines():
  c, d, ok, why = (l.split('\t') + [''])[:4]; S[c].append((int(d[8:]), int(ok), why))
rows = D['kkh'][M]; n_up = 0; skip = sorted(c for c in S if c not in {cc[x[0]] for x in rows if R[x[1]]['code'].startswith('197')})
for x in rows:
  code = cc[x[0]]
  if not R[x[1]]['code'].startswith('197'): continue
  wk, why = [None] * 5, [''] * 5
  for w in range(5):
    ph = [p for p in S.get(code, []) if wkOf(p[0]) == w]
    if ph:
      wk[w] = 1 if any(p[1] for p in ph) else 0
      why[w] = '' if wk[w] else ', '.join(dict.fromkeys(p[2] for p in ph if p[2]))
    elif WEND[w] < TODAY: wk[w], why[w] = 0, 'Không chụp ảnh'
  n = sum(1 for v in wk if v == 1)
  x[:] = [x[0], x[1], n, 1 if n >= 3 else 0, x[4], wk, why]; n_up += 1
print('cập nhật', n_up, 'KH; DMS ngoài danh sách', skip)
K = [x for x in rows if R[x[1]]['code'].startswith('197')]
print('đạt theo tuần', [sum(1 for x in K if x[5][w] == 1) for w in range(5)], 'rớt', [sum(1 for x in K if x[5][w] == 0) for w in range(5)], 'đạt ≥3', sum(x[3] for x in K), 'đạt ≥1', sum(1 for x in K if x[2] >= 1))
print(collections.Counter(R[x[1]]['code'] for x in K if x[2] >= 1))
s = s[:i] + json.dumps(D, ensure_ascii=False, separators=(',', ':')) + s[j:]; open(P, 'w', encoding='utf8').write(s)

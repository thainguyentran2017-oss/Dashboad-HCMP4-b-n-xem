# Tìm ảnh cùng không gian giữa các KH khác nhau: ORB + RANSAC trên ảnh thu nhỏ
import glob, os, cv2, numpy as np, json, sys
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kimg')
rows = []
for f in sorted(glob.glob(os.path.join(D, 'meta*.txt'))):
  pg = int(os.path.basename(f)[4:6])
  for l in open(f):
    i, c, dt, h, o = l.strip().split('|'); rows.append(dict(c=c, dt=dt, f='p%02d_%02d.jpg' % (pg, int(i))))
orb = cv2.ORB_create(1500); bf = cv2.BFMatcher(cv2.NORM_HAMMING)
for r in rows:
  g = cv2.imread(os.path.join(D, r['f']), cv2.IMREAD_GRAYSCALE); g = cv2.resize(g, None, fx=1.5, fy=1.5)
  r['kp'], r['ds'] = orb.detectAndCompute(g, None)
res = []
for a in range(len(rows)):
  A = rows[a]
  if A['ds'] is None: continue
  for b in range(a + 1, len(rows)):
    B = rows[b]
    if A['c'] == B['c'] or B['ds'] is None: continue
    m = bf.knnMatch(A['ds'], B['ds'], k=2); good = [x[0] for x in m if len(x) == 2 and x[0].distance < 0.75 * x[1].distance]
    if len(good) < 12: continue
    p1 = np.float32([A['kp'][g.queryIdx].pt for g in good]); p2 = np.float32([B['kp'][g.trainIdx].pt for g in good])
    H, mask = cv2.findHomography(p1, p2, cv2.RANSAC, 6.0)
    inl = int(mask.sum()) if mask is not None else 0
    if inl >= 15: res.append((inl, len(good), A['c'], A['dt'], A['f'], B['c'], B['dt'], B['f']))
res.sort(reverse=True)
for x in res[:60]: print(x)
print(len(res)); json.dump(res, open(os.path.join(D, 'dup.json'), 'w'))

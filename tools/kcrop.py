# kcrop.py <page> <shot0> [shot1] [shot2]  → kimg/p<page>_<idx>.jpg (360 px wide grid cells, black bars trimmed)
import sys, os
from PIL import Image, ImageOps
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kimg'); pg = int(sys.argv[1])
n = sum(1 for _ in open(os.path.join(D, 'meta%02d.txt' % pg)))
for s, path in enumerate(sys.argv[2:]):
  im = Image.open(path).convert('RGB')
  for j in range(8):
    k = s * 8 + j
    if k >= n: break
    c = im.crop(((j % 4) * 360, (j // 4) * 270, (j % 4) * 360 + 360, (j // 4) * 270 + 270))
    bb = ImageOps.invert(c.convert('L')).point(lambda v: 255 if v < 245 else 0).getbbox()  # non-black area
    if bb: c = c.crop(bb)
    c.save(os.path.join(D, 'p%02d_%02d.jpg' % (pg, k)), quality=72)
print('page', pg, 'rows', n)

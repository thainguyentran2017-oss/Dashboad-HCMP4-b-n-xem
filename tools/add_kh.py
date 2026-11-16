# Danh sách KH tháng (file Danh sách khách hàng) → routes[].kh (đúng thứ tự file), custInfo [tên, địa chỉ, loại hình, seg, thứ]
import pandas as pd, json, re, sys, collections
SRC=sys.argv[1]; P='/home/claude/sdo-de.html'
s=open(P,encoding='utf8').read(); i=s.index('const DATA = '); j=s.index(';</script>',i); D=json.loads(s[i+13:j])
d=pd.read_excel(SRC,dtype=str).fillna('')
CC={c:k for k,c in enumerate(D['custCodes'])}; RI={r['code']:k for k,r in enumerate(D['routes'])}
bad=sorted(set(d['Mã Route'])-set(RI))
if bad: print('UNKNOWN routes',bad); sys.exit(1)
st=collections.Counter(); newc=[]
for _,x in d.iterrows():
  kh=x['Mã KH'].strip(); thu=','.join(re.findall(r'\d',x['Sub Route']))
  info=[x['Tên KH'],x['Địa Chỉ'],x['Loại Hình'],x['Segment'],thu]
  if kh not in CC: CC[kh]=len(D['custCodes']); D['custCodes'].append(kh); D['custInfo'].append(info); newc.append(kh); continue
  ci=D['custInfo'][CC[kh]]
  for k,n in [(4,'thu'),(1,'addr'),(3,'seg'),(2,'lh'),(0,'name')]:
    if ci[k]!=info[k]: st[n]+=1; ci[k]=info[k]
added=collections.Counter(); moved=0
for rt,g in d.groupby('Mã Route',sort=False):
  r=D['routes'][RI[rt]]; L=[CC[c.strip()] for c in g['Mã KH']]; old=set(r.get('kh',[]))
  added[r['npp']]+=sum(1 for c in L if c not in old); r['kh']=L
print('KH',len(d),'routes',d['Mã Route'].nunique(),'mới trong DS tuyến',dict(added),'mã KH mới hoàn toàn',len(newc),'đổi',dict(st))
s=s[:i]+'const DATA = '+json.dumps(D,ensure_ascii=False,separators=(',',':'))+s[j:]
open(P,'w',encoding='utf8').write(s)

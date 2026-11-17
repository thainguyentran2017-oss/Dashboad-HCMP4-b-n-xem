# DS KH TH Segment D được tham gia Trưng bày Tết → DATA.tbD (chỉ số KH)
import pandas as pd, json, sys
SRC=sys.argv[1]; P='/home/claude/sdo-de.html'
s=open(P,encoding='utf8').read(); i=s.index('const DATA = '); j=s.index(';</script>',i); D=json.loads(s[i+13:j])
CC={c:k for k,c in enumerate(D['custCodes'])}
d=pd.read_excel(SRC,dtype=str).fillna(''); L=[]; newc=0
for _,r in d.iterrows():
  kh=r['OutletCode'].strip().upper()
  if not kh: continue
  if kh not in CC: CC[kh]=len(D['custCodes']); D['custCodes'].append(kh); D['custInfo'].append([r['OutletName'],'',r['OutletTypeDetail'],r['Segment'],'']); newc+=1
  L.append(CC[kh])
D['tbD']=sorted(set(L)); s=s[:i]+'const DATA = '+json.dumps(D,ensure_ascii=False,separators=(',',':'))+s[j:]; open(P,'w',encoding='utf8').write(s)
print('tbD',len(D['tbD']),'new codes',newc)

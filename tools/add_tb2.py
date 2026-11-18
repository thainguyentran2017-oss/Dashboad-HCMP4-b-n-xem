# DS ASO tham gia Trưng bày Tết (file DPM) → DATA.tb.rows ; in thay đổi so với hiện tại; 'apply' để ghi
import pandas as pd, json, sys, collections
SRC=sys.argv[1]; APPLY='apply' in sys.argv; P='/home/claude/sdo-de.html'
s=open(P,encoding='utf8').read(); i=s.index('const DATA = '); j=s.index(';</script>',i); D=json.loads(s[i+13:j])
d=pd.read_excel(SRC,header=3,dtype=str).fillna(''); d=d[d['Mã Khách Hàng'].str.strip()!='']
CC={c:k for k,c in enumerate(D['custCodes'])}; RI={r['code']:k for k,r in enumerate(D['routes'])}
old={(D['custCodes'][x[0]],D['routes'][x[1]]['code']):x for x in D['tb']['rows']}
rows=[]; bad=[]; newc=0
for _,r in d.iterrows():
  kh=r['Mã Khách Hàng'].strip().upper(); rt=r['Mã Route'].strip()
  if rt not in RI: bad.append((kh,rt)); continue
  if kh not in CC:
    CC[kh]=len(D['custCodes']); D['custCodes'].append(kh); D['custInfo'].append([r['Tên Khách Hàng'],r['Địa Chỉ'],r['Loại Hinh'],r['Segment'],'']); newc+=1
  t=float(r['Chỉ Tiêu (Đ/v các CT DCR tự nhập chỉ tiêu)'].replace(',','') or 0)
  rows.append([CC[kh],RI[rt],t,1 if r['Trạng Thái']=='Da Duyet' else 0,r['Ngày DCR Đăng Ký'][:10],r['Loại Hinh'],r['Segment'],r['Mức Tham Gia'].replace('TB Tết P1_','')])
new={(D['custCodes'][x[0]],D['routes'][x[1]]['code']):x for x in rows}
NPP=lambda k: D['routes'][RI[k[1]]]['npp']
add=[k for k in new if k not in old]; rem=[k for k in old if k not in new]
ch=collections.Counter()
for k in new:
  if k in old and new[k][2:]!=old[k][2:]:
    o,n=old[k],new[k]
    if o[3]!=n[3]: ch['duyet' if n[3] else 'bo duyet']+=1
    if o[7]!=n[7]: ch['muc '+o[7]+'->'+n[7]]+=1
    if o[2]!=n[2]: ch['ct']+=1
print('dup',len(rows)-len(new),'add',len(add),'rem',len(rem),dict(ch),'bad',bad[:5],len(bad),'newc',newc)
print('add by NPP',collections.Counter(NPP(k) for k in add)); print('rem by NPP',collections.Counter(NPP(k) for k in rem)); print('rem',rem[:20])
f=lambda R:(len(R),sum(x[3] for x in R),dict(collections.Counter(x[7] for x in R)))
print('cũ',f(list(old.values()))); print('mới',f(rows))
if APPLY:
  D['tb']['rows']=rows; D['tb']['code']=d['Mã Chương Trình'].iloc[0]
  s=s[:i]+'const DATA = '+json.dumps(D,ensure_ascii=False,separators=(',',':'))+s[j:]; open(P,'w',encoding='utf8').write(s); print('applied')

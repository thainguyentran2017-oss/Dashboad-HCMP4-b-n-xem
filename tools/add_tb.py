# DS ASO tham gia Trưng bày Tết GĐ1 (file DPM) → DATA.tb
import pandas as pd, json, sys, collections
SRC=sys.argv[1]; P='/home/claude/sdo-de.html'
s=open(P,encoding='utf8').read(); i=s.index('const DATA = '); j=s.index(';</script>',i); D=json.loads(s[i+13:j])
d=pd.read_excel(SRC,header=3,dtype=str).fillna('')
CC={c:k for k,c in enumerate(D['custCodes'])}; RI={r['code']:k for k,r in enumerate(D['routes'])}
rows=[]; bad=[]; newc=0
for _,r in d.iterrows():
  kh=r['Mã Khách Hàng'].strip().upper(); rt=r['Mã Route'].strip()
  if rt not in RI: bad.append((kh,rt)); continue
  if kh not in CC:
    CC[kh]=len(D['custCodes']); D['custCodes'].append(kh); D['custInfo'].append([r['Tên Khách Hàng'],r['Địa Chỉ'],r['Loại Hinh'],r['Segment'],'']); newc+=1
  t=float(r['Chỉ Tiêu (Đ/v các CT DCR tự nhập chỉ tiêu)'].replace(',','') or 0)
  rows.append([CC[kh],RI[rt],t,1 if r['Trạng Thái']=='Da Duyet' else 0,r['Ngày DCR Đăng Ký'][:10],r['Loại Hinh'],r['Segment'],r['Mức Tham Gia'].replace('TB Tết P1_','')])
D['tb']={'code':d['Mã Chương Trình'].iloc[0],'name':d['Tên Chương Trình'].iloc[0],'m':'2026-11','d1':9,'d2':22,'rows':rows}
s=s[:i]+'const DATA = '+json.dumps(D,ensure_ascii=False,separators=(',',':'))+s[j:]
open(P,'w',encoding='utf8').write(s)
print('rows',len(rows),'duyệt',sum(x[3] for x in rows),'bad',bad[:5],len(bad),'new codes',newc, collections.Counter(x[7] for x in rows))

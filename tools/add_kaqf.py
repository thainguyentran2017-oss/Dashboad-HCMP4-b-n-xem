# DS ASO tham gia Trưng bày khối AQF (file DPM, header dòng 4) → DATA.kaqf ; 'apply' để ghi
import pandas as pd, json, sys, collections
SRC=sys.argv[1]; APPLY='apply' in sys.argv; P='/home/claude/sdo-de.html'
s=open(P,encoding='utf8').read(); i=s.index('const DATA = '); j=s.index(';</script>',i); D=json.loads(s[i+13:j])
d=pd.read_excel(SRC,header=3,dtype=str).fillna(''); d=d[d['Mã Khách Hàng'].str.strip()!='']
CC={c:k for k,c in enumerate(D['custCodes'])}; RI={r['code']:k for k,r in enumerate(D['routes'])}
old={D['custCodes'][x[0]]:x for x in (D.get('kaqf') or {}).get('rows',[])}
rows=[]; bad=[]; newc=0
for _,r in d.iterrows():
  kh=r['Mã Khách Hàng'].strip().upper(); rt=r['Mã Route'].strip()
  if rt not in RI: bad.append((kh,rt)); continue
  if kh not in CC:
    CC[kh]=len(D['custCodes']); D['custCodes'].append(kh); D['custInfo'].append([r['Tên Khách Hàng'],r['Địa Chỉ'],r['Loại Hinh'],r['Segment'],'']); newc+=1
  t=float(r['Chỉ Tiêu (Đ/v các CT DCR tự nhập chỉ tiêu)'].replace(',','') or 0)
  lv=r['Mức Tham Gia'].replace('TB Khối AQF_','').strip()
  rows.append([CC[kh],RI[rt],t,1 if r['Trạng Thái']=='Da Duyet' else 0,r['Ngày DCR Đăng Ký'][:10],r['Loại Hinh'],r['Segment'],lv])
new={D['custCodes'][x[0]]:x for x in rows}
print('rows',len(rows),'uniq',len(new),'bad',bad,'newc',newc,'add',len([k for k in new if k not in old]),'rem',len([k for k in old if k not in new]))
print(collections.Counter(x[7] for x in rows), collections.Counter(D['routes'][x[1]]['npp'] for x in rows), 'ct',sum(x[2] for x in rows))
if APPLY:
  D['kaqf']={'code':d['Mã Chương Trình'].iloc[0],'name':d['Tên Chương Trình'].iloc[0],'m':'2026-11','rows':rows}
  s=s[:i]+'const DATA = '+json.dumps(D,ensure_ascii=False,separators=(',',':'))+s[j:]; open(P,'w',encoding='utf8').write(s); print('applied')

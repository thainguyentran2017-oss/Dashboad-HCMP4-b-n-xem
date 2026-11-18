# DS KH tham gia "Tích lũy AQF 500ml" (file TRACKING, sheet DPM) → DATA.a5 ; in ra thay đổi so với hiện tại
import pandas as pd, json, sys, collections
SRC=sys.argv[1]; APPLY=len(sys.argv)>2; P='/home/claude/sdo-de.html'
s=open(P,encoding='utf8').read(); i=s.index('const DATA = '); j=s.index(';</script>',i); D=json.loads(s[i+13:j])
for h in (1,3,0,2):
  d=pd.read_excel(SRC,sheet_name='DPM',header=h,dtype=str).fillna('')
  if 'Mã Khách Hàng' in d.columns: break
d=d.rename(columns={c:'Chỉ tiêu' for c in d.columns if str(c).startswith('Chỉ Tiêu') or str(c)=='Chỉ tiêu'})
d=d[d['Mã Khách Hàng'].str.strip()!='']
CC={c:k for k,c in enumerate(D['custCodes'])}; RI={r['code']:k for k,r in enumerate(D['routes'])}
old={(D['custCodes'][x[0]],D['routes'][x[1]]['code']):x for x in D['a5']['rows']}
rows=[]; bad=[]; newc=0
for _,r in d.iterrows():
  kh=r['Mã Khách Hàng'].strip().upper(); rt=r['Mã Route'].strip()
  if rt not in RI: bad.append((kh,rt)); continue
  if kh not in CC:
    CC[kh]=len(D['custCodes']); D['custCodes'].append(kh); D['custInfo'].append([r['Tên Khách Hàng'],r['Địa Chỉ'],r['Loại Hinh'],r['Segment'],'']); newc+=1
  rows.append([CC[kh],RI[rt],float(r['Chỉ tiêu'].replace(',','') or 0),1 if r['Trạng Thái']=='Da Duyet' else 0,r['Ngày DCR Đăng Ký'][:10],r['Loại Hinh']])
new={(D['custCodes'][x[0]],D['routes'][x[1]]['code']):x for x in rows}
for k in new:
  if k not in old: print('THÊM',k,new[k])
for k in old:
  if k not in new: print('BỎ',k,old[k])
for k in new:
  if k in old and new[k][2:]!=old[k][2:]: print('ĐỔI',k,old[k][2:],'->',new[k][2:])
f=lambda R:(len(R),sum(x[3] for x in R),sum(x[2] for x in R))
print('cũ (dòng, duyệt, CT)',f(list(old.values())),'mới',f(rows),'bad',bad,'new codes',newc)
if APPLY:
  D['a5'].update({'code':d['Mã Chương Trình'].iloc[0],'name':d['Tên Chương Trình'].iloc[0],'rows':rows})
  s=s[:i]+'const DATA = '+json.dumps(D,ensure_ascii=False,separators=(',',':'))+s[j:]; open(P,'w',encoding='utf8').write(s); print('applied')

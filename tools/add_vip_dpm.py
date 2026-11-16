import pandas as pd, json, collections, sys
SRC=sys.argv[1]; M=sys.argv[2]; P='/home/claude/sdo-de.html'; APPLY=len(sys.argv)>3
s=open(P,encoding='utf8').read(); i=s.index('const DATA = '); j=s.index(';</script>',i); D=json.loads(s[i+13:j])
d=pd.read_excel(SRC,header=3,dtype=str).fillna('')
CC={c:k for k,c in enumerate(D['custCodes'])}; RI={r['code']:k for k,r in enumerate(D['routes'])}
num=lambda v: float(str(v).replace(',','').strip() or 0)
K={}; bad=[]; newc=[]
for _,r in d.iterrows():
  kh=r['Mã Khách Hàng'].strip().upper(); rt=r['Mã Route'].strip()
  if rt not in RI: bad.append((kh,rt)); continue
  if kh not in CC:
    CC[kh]=len(D['custCodes']); D['custCodes'].append(kh); D['custInfo'].append([r['Tên Khách Hàng'],r['Địa Chỉ'],r['Loại Hinh'],r['Segment'],'']); newc.append(kh)
  o=K.setdefault(kh,{'ri':RI[rt],'lh':r['Loại Hinh'],'t1':0,'t2':0,'s1':'','s2':''})
  if r['Mức Tham Gia']=='LRB-AQF': o['t1']=num(r['Chỉ Tiêu (Đ/v các CT DCR tự nhập chỉ tiêu)']); o['s1']=r['Trạng Thái']
  elif r['Mức Tham Gia']=='LRB CAN': o['t2']=num(r['Chỉ Tiêu (Đ/v các CT DCR tự nhập chỉ tiêu)']); o['s2']=r['Trạng Thái']
rows=[]
for kh,o in K.items():
  pend=[n for n,st in [('LRB-AQF',o['s1']),('LRB CAN',o['s2'])] if st and st!='Da Duyet']
  ok=1 if o['s1']=='Da Duyet' else 0
  note='' if not pend else ' · '.join(n+' chờ duyệt' for n in pend) if all(o['s'+str(k)] for k in (1,2)) or pend else ''
  if not o['s1']: note=(note+' · ' if note else '')+'Chưa đăng ký LRB-AQF'
  V={'Da Duyet':'Đã duyệt','Cho Duyet':'Chờ duyệt'}; a=V.get(o['s1'],o['s1']); b=V.get(o['s2'],o['s2'])
  st=a if a==b else ' · '.join(x for x in [('AQF: '+a) if a else '',('CAN: '+b) if b else ''] if x)
  rows.append([CC[kh],o['ri'],o['lh'],o['t1'],o['t2'],0,0,ok,note,st])
old={x[0]:x for x in D['titan'].get(M,[])}; new={x[0]:x for x in rows}
add=[c for c in new if c not in old]; rem=[c for c in old if c not in new]; chg=[c for c in new if c in old and (old[c][3],old[c][4])!=(new[c][3],new[c][4])]
print('KH',len(rows),'hợp lệ (LRB-AQF đã duyệt)',sum(x[7] for x in rows),'chờ duyệt có',sum(1 for x in rows if 'chờ' in x[8]),'bad routes',bad[:5],len(bad),'new codes',len(newc))
print('old',len(old),'add',len(add),'removed',len(rem),'target changed',len(chg))
print('sum t1',sum(x[3] for x in rows),'t2',sum(x[4] for x in rows),'| old',sum(x[3] for x in old.values()),sum(x[4] for x in old.values()))
print('only AQF',sum(1 for o in K.values() if o['s1'] and not o['s2']),'only CAN',sum(1 for o in K.values() if o['s2'] and not o['s1']))
by=collections.Counter(D['routes'][x[1]]['npp'] for x in rows); print(by)
print('samples chg',[(D['custCodes'][c],old[c][3:5],new[c][3:5]) for c in chg[:5]])
if APPLY:
  D['titan'][M]=rows
  s=s[:i]+'const DATA = '+json.dumps(D,ensure_ascii=False,separators=(',',':'))+s[j:]
  open(P,'w',encoding='utf8').write(s); print('applied')

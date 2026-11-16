# Báo cáo Kỷ luật Route (RP2019) → DATA.klr[m] = {r, v, t, kd, vd, ts, tr, miss}
import openpyxl, json, sys, datetime, collections
SRC=sys.argv[1]; M=sys.argv[2]; P='/home/claude/sdo-de.html'; DRY='--dry' in sys.argv
s=open(P,encoding='utf8').read(); i=s.index('const DATA = '); j=s.index(';</script>',i); D=json.loads(s[i+13:j])
CC={c:k for k,c in enumerate(D['custCodes'])}; RI={r['code']:k for k,r in enumerate(D['routes'])}
old=D['klr'].get(M,{})
wb=openpyxl.load_workbook(SRC,read_only=True,data_only=True)
num=lambda v: float(v) if isinstance(v,(int,float)) else 0.0
X=lambda v: 1 if v=='x' else 0
mins=lambda t: t.hour*60+t.minute if isinstance(t,datetime.datetime) else ''
secs=lambda t: t.hour*3600+t.minute*60+t.second
R=[]; kd=set(); unk=set()
for r in wb['Kỷ Luật Route'].iter_rows(min_row=1,values_only=True):
  if not isinstance(r[0],datetime.datetime) or r[0].strftime('%Y-%m')!=M: continue
  ri=RI.get(r[6]); 
  if ri is None: unk.add(r[6]); continue
  d=r[0].day; kd.add(d)
  R.append([d,ri,num(r[9]),num(r[10]),num(r[11]),num(r[12]),num(r[13]),num(r[14]),num(r[15]),num(r[16]),num(r[17]),num(r[18]),round(num(r[19]),1),num(r[20]),num(r[21]),X(r[22]),X(r[23]),X(r[24]),X(r[25]),mins(r[26]),mins(r[27]),X(r[28]),X(r[29])])
TS=old.get('ts') or ['< 1ph','< 3ph','< 5ph','< 10ph','10ph-60ph','> 60ph']; TR=list(old.get('tr') or [])
T=[]; V=collections.Counter(); vd=set()
for r in wb['Viếng Thăm Chi Tiết'].iter_rows(min_row=1,values_only=True):
  if not isinstance(r[0],datetime.datetime) or r[0].strftime('%Y-%m')!=M or not r[10] or not isinstance(r[14],datetime.datetime) or (secs(r[14])==0 and secs(r[15])==0): continue
  ri=RI.get(r[6])
  if ri is None: unk.add(r[6]); continue
  d=r[0].day; vd.add(d); kh=str(r[10]).strip(); c=CC.get(kh)
  if c is None: CC[kh]=c=len(D['custCodes']); D['custCodes'].append(kh); D['custInfo'].append([r[11] or '',r[13] or '',r[12] or '','',''])
  il=1 if r[28]=='x' else 0; lan=int(r[9] or 1)
  if num(r[30])>0: V[(d,ri,0 if il else 1,lan)]+=1
  sl=TS.index(r[37]) if r[37] in TS else -1
  lk=str(r[47] or '')
  if not lk.startswith('http'): lk=''
  else:
    fo,fn=lk.split('/')[-2:]
    lk='~'+fn[len(kh):].rsplit('.',1)[0] if fo==r[0].strftime('%Y%m%d') and fn.startswith(kh) and fn.lower().endswith('.jpg') and lk.startswith('https://spvbpicture.blob.core.windows.net/picture-review/') else ('!'+fo+'/'+fn if lk.startswith('https://spvbpicture.blob.core.windows.net/picture-review/') else lk)
  rs=str(r[48] or '').strip(); rn=-1
  if rs:
    if rs not in TR: TR.append(rs)
    rn=TR.index(rs)
  sf=r[16]; sf=round((sf-datetime.datetime(1899,12,30)).total_seconds())%86400 if isinstance(sf,datetime.datetime) else -1
  T.append([d,ri,c,secs(r[14]),secs(r[15]),lan,sl,lk,rn,il,sf])
T.sort(key=lambda x:(x[1],x[0],x[3]))
K={'r':R,'v':[[a,b,c,e,n] for (a,b,c,e),n in sorted(V.items())],'kd':sorted(kd),'vd':sorted(vd),'t':T,'ts':TS,'tr':TR,'miss':sorted(kd-vd)}
print('KLR',M,'route-days',len(R),'days KLR',K['kd'][-1:],'visit',K['vd'][-1:],'visits',len(T),'unknown routes',unk)
if DRY: json.dump(K,open('klr_dry.json','w'),ensure_ascii=False); sys.exit()
for k,v in old.items():
  if k not in K: K[k]=v
D['klr'][M]=K
s=s[:i]+'const DATA = '+json.dumps(D,ensure_ascii=False,separators=(',',':'))+s[j:]
open(P,'w',encoding='utf8').write(s); print('applied')

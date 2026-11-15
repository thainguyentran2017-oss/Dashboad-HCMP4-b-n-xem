# Splice one NPP's current-month Rawdata (xlsx) into DATA, re-encoding every rawdata-derived array for that NPP's routes.
import pandas as pd, json, collections, re, sys, unicodedata, datetime
SRC, NPP = sys.argv[1], sys.argv[2]
P='/home/claude/sdo-de.html'
html=open(P,encoding='utf8').read(); i=html.index('const DATA = '); j=html.index(';</script>',i); D=json.loads(html[i+13:j])
nf=lambda v: unicodedata.normalize('NFC',v) if isinstance(v,str) else v
d=pd.read_excel(SRC,dtype=object); d.columns=[nf(c) for c in d.columns]
for c in d.columns:
  if d[c].dtype==object: d[c]=d[c].map(nf)
d=d[d['Tên NPP']==NPP].copy()
M=D['dates'][-1][:7]; y,mo=map(int,M.split('-'))
d=d[d['Ngày (Đơn Hàng)'].map(lambda t: t.year==y and t.month==mo)]
CC={c:i for i,c in enumerate(D['custCodes'])}; RI={r['code']:i for i,r in enumerate(D['routes'])}; SK={n:i for i,n in enumerate(D['skuNames'])}
miss_r=set(d['Mã Route'])-set(RI); miss_s=set(d['Tên SP'])-set(SK)
if miss_r or miss_s: print('UNKNOWN routes',miss_r,'skus',miss_s); sys.exit(1)
NR={i for i,r in enumerate(D['routes']) if r['npp']==NPP}
# new customers
LH={}
for c,lh in zip(d['Mã KH'],d['Mã Loại Hình']):
  k=CC.get(c)
  if k is not None: LH.setdefault(lh,collections.Counter())[D['custInfo'][k][2]]+=1
newc=[]
for _,r in d.drop_duplicates('Mã KH').iterrows():
  c=r['Mã KH']
  if c in CC: continue
  CC[c]=len(D['custCodes']); D['custCodes'].append(c)
  ph=lambda s: re.sub(r'^\S+ - (Xã|Phường|Thị trấn|Thị Trấn)\s*','',str(s or ''))
  D['custInfo'].append([r['Tên KH'] or '', ' - '.join(str(x) for x in [r['Số Nhà'],r['Đường'],ph(r['Phường'])] if x not in (None,'')), (LH.get(r['Mã Loại Hình']) or collections.Counter({'TH':1})).most_common(1)[0][0], r['Customer Segment'] or '', ''])
  newc.append(c)
fac=lambda n: .5 if re.search(r'(1500|2000).*(6 chai|x6)',n) else 1
d['c']=d['Mã KH'].map(CC.get); d['ri']=d['Mã Route'].map(RI.get); d['di']=d['Ngày (Đơn Hàng)'].map(lambda t:t.day-1); d['day']=d['di']+1
d['f']=d['Tên SP'].map(fac); num=lambda s: s.fillna(0).astype(float)
d['qd']=num(d['Sản lượng đi giao']); d['q']=d['qd']*d['f']; d['qo']=num(d['Sản lượng đặt hàng'])*d['f']; d['qt']=num(d[' Sản lượng thực giao'] if ' Sản lượng thực giao' in d else d['Sản lượng thực giao'])*d['f']
d['k']=d['Tên SP'].map(SK); d['ctkm']=d['Mã CTKM'].fillna('').map(lambda s: set(str(s).split('\\')))
CAT={c:i for i,c in enumerate(D['cats'])}; d['cat']=d['Tên Ngành Hàng'].fillna('').map(lambda c: CAT.get(c,CAT['KHÁC']))
rd=lambda v: round(float(v),4)
drop=lambda key,pos: [x for x in D[key] if x[pos] not in NR]
# skuEv
g=d.groupby(['c','ri','di','k'])['q'].sum(); D['skuEv']=drop('skuEv',1)+[[int(a),int(b),int(c),int(k),rd(v)] for (a,b,c,k),v in g.items() if v]
# events: Revive ≥1 thùng/đơn → bit 1|2, Tea+ → 4, DE promo → 8
F=collections.defaultdict(int)
for (o,c,ri,di,b),q in d.groupby(['Mã Đơn Hàng','c','ri','di','Nhãn Hàng'])['q'].sum().items():
  if q>=1 and b=='REVIVE': F[(c,ri,di)]|=3
  if q>=1 and b=='TEA+': F[(c,ri,di)]|=4
PR=set(D['promo'])
for _,r in d[(d.qd>0)&d.ctkm.map(lambda s: bool(s&PR))].iterrows(): F[(r.c,r.ri,r.di)]|=8
D['events']=drop('events',1)+[[int(a),int(b),int(c),f] for (a,b,c),f in F.items()]
# vol / ord / ordx / aqua / tg / dh
g=d.groupby(['ri','di','cat']).agg(q=('q','sum'),r=('DS Sau Chiết Khấu /KM',lambda s: num(s).sum()))
D['vol']=drop('vol',0)+[[int(a),int(b),int(c),rd(x.q),int(round(x.r))] for (a,b,c),x in g.iterrows() if x.q or x.r]
D['ord']=drop('ord',0)+[[int(a),int(b),int(n)] for (a,b),n in d.groupby(['ri','di'])['Mã Đơn Hàng'].nunique().items()]
od=d.groupby(['ri','di','Mã Đơn Hàng'])['Trái Tuyến'].agg(lambda s: bool(s.fillna(False).astype(bool).any()))
out=od.groupby(level=[0,1]).sum(); ln=d.groupby(['ri','di']).size()
D['ordx']=drop('ordx',0)+[[int(a),int(b),int(out.get((a,b),0)),int(n)] for (a,b),n in ln.items()]
D['aqua']=drop('aqua',0)+[[int(a),int(b),rd(v)] for (a,b),v in d[d['Nhãn Hàng']=='AQUAFINA'].groupby(['ri','di'])['q'].sum().items() if v]
D['tg']=drop('tg',0)+[[int(a),int(b),rd(v)] for (a,b),v in d.groupby(['ri','di'])['qt'].sum().items() if v]
D['dh']=drop('dh',0)+[[int(a),int(b),rd(v)] for (a,b),v in d.groupby(['ri','di'])['qo'].sum().items() if v]
# nw: opened this month, first day with an order
x=d[d['Ngày mở mới'].map(lambda t: hasattr(t,'year') and t.year==y and t.month==mo) & (d.qd>0)]
D['nw']=drop('nw',1)+[[int(c),int(ri),int(di)] for (c,ri),di in x.groupby(['c','ri'])['di'].min().items()]
# DE packages (gói DE T11): slots 0/1 OFF, 2/3 ON; slot 3 không tính thùng 28 lon
T=[[['7UP','MIRINDA','BOSS','ROCKSTAR'],['PEPSI'],['STING'],['TEA+'],['REVIVE','TWISTER']],
   [['7UP','MIRINDA','BOSS','ROCKSTAR','TWISTER'],['PEPSI'],['STING'],['REVIVE','TEA+'],['AQUAFINA']],
   [['PEPSI'],['7UP','MIRINDA','TWISTER'],['STING','ROCKSTAR'],['TEA+','REVIVE','AQUAFINA','BOSS']],
   [['PEPSI','7UP','MIRINDA'],['STING','ROCKSTAR'],['TEA+','BOSS'],['REVIVE','TWISTER']]]
NM=[['7Up/Mirinda/Boss/Rockstar','Pepsi','Sting','Tea+','Revive/Twister/Good Mood'],['7Up/Mirinda/Boss/Rockstar/Twister/Good Mood','Pepsi','Sting','Revive/Tea+','Aquafina'],
    ['Pepsi','7Up/Mirinda/Twister/Good Mood','Sting/Rockstar','Tea+/Revive/Aquafina/Boss'],['Pepsi/7Up/Mirinda','Sting/Rockstar','Tea+/Boss','Revive/Twister/Good Mood']]
pk=set(); best={}
for (o,c,ri,di),g in d.groupby(['Mã Hóa Đơn','c','ri','di']):
  if g['Customer Segment'].iloc[0] not in ('D','E'): continue
  on=g['Mã Kênh Phụ'].iloc[0]=='ON'; qb=g.groupby('Nhãn Hàng')['q'].sum(); qb28=g[~g['Tên SP'].str.contains('x28')].groupby('Nhãn Hàng')['q'].sum()
  for s in ([2,3] if on else [0,1]):
    Q=qb28 if s==3 else qb; mk=0
    for t,tier in enumerate(T[s]):
      if sum(Q.get(b,0) for b in tier)<1: mk|=1<<t
    n=bin(mk).count('1')
    if 1<=n<=2: pk.add((int(c),int(ri),int(di),s,mk))
    best.setdefault((c,ri,di),[]).append((n,s,' + '.join(NM[s][t] for t in range(5) if mk>>t&1)))
D['dePk']=drop('dePk',1)+[list(x) for x in sorted(pk)]
LAB=D['deMissLab']; dm=[]
for (c,ri,di),v in best.items():
  n,s,l=sorted(v)[0]
  if 1<=n<=2:
    if l not in LAB: LAB.append(l)
    dm.append([int(c),int(ri),int(di),n,LAB.index(l)])
D['deMiss']=drop('deMiss',1)+dm
# Tăng tồn & Combo Tea+ (per order with the CTKM code)
for key,cnt in [('tt','minQ'),('cb','set')]:
  X=D[key]; code=X['code']; per=X[cnt]
  if key=='cb' and M not in X['ms']: continue
  rows=[]
  for (o,c,ri,day),g in d[d.ctkm.map(lambda s: code in s)].groupby(['Mã Đơn Hàng','c','ri','day']):
    q=g.qd.sum(); rows.append([int(c),int(ri)]+([X['ms'].index(M)] if key=='cb' else [])+[int(day),rd(q),int(q//per)])
  X['ev']=[e for e in X['ev'] if not (e[1] in NR and (key!='cb' or e[2]==X['ms'].index(M)))]+rows
# customer channel sets / open dates
on=set(d.loc[d['Mã Kênh Phụ'].isin(['ON','Food Delivery']),'c']); D['custOn']=sorted(set(D['custOn'])|{int(c) for c in on}); D['custOnK']=sorted(set(D['custOnK'])|{int(c) for c in on})
b2b=set(d.loc[d['Mã Kênh Phụ'].isin(['B2B','eB2B']),'c']); D['custB2B']=sorted(set(D['custB2B'])|{int(c) for c in b2b})
for c,t in d.drop_duplicates('c')[['c','Ngày mở mới']].values:
  if hasattr(t,'year') and t>=datetime.datetime(y,mo,1)-datetime.timedelta(days=190) and str(int(c)) not in D['custOpen']: D['custOpen'][str(int(c))]=t.strftime('%Y-%m-%d')
# dates / rawLast / updated
last=d['Ngày (Đơn Hàng)'].max().strftime('%Y-%m-%d')
while D['dates'][-1]<last:
  nd=(datetime.date.fromisoformat(D['dates'][-1])+datetime.timedelta(days=1)).isoformat(); D['dates'].append(nd)
D['rawLast']['d'][NPP]=last; D['updated']=max(D['updated'],last)
html=html[:i]+'const DATA = '+json.dumps(D,ensure_ascii=False,separators=(',',':'))+html[j:]
open(P,'w',encoding='utf8').write(html)
print('NPP',NPP,'rows',len(d),'days',sorted(d.day.unique()),'last',last,'new cust',newc,'events',len(F),'dePk',len(pk),'deMiss',len(dm),'labels',len(LAB))
print('dates',D['dates'][-1],'rawLast',D['rawLast']['d'])

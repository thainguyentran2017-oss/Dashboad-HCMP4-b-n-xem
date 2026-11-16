# Update the rawdata columns (SL MTD, DE, SDO 1, SDO 2, Rockstar, Boss, Sting Vàng Pro, Sữa trái cây) of bh/data.json from DATA
import json, collections
P='/home/claude/sdo-de.html'; F='/home/claude/dashboad-hcmp4-b-n-xem/bh/data.json'
s=open(P,encoding='utf8').read(); i=s.index('const DATA = '); j=s.index(';</script>',i); D=json.loads(s[i+13:j])
B=json.load(open(F)); CC=D['custCodes']; SN=D['skuNames']; BR=D['brands']; SB=D['skuBrand']
q=collections.defaultdict(float); fl=collections.defaultdict(int); has=collections.defaultdict(set)
brand=lambda k: BR[SB[k][0]] if SB[k] and SB[k][0] is not None and SB[k][0] < len(BR) else ''
for c,ri,di,k,v in D['skuEv']:
  if v<=0: continue
  cc=CC[c]; q[cc]+=v; b=brand(k).upper()
  if b=='ROCKSTAR': has[cc].add(14)
  if b=='BOSS': has[cc].add(15)
  if 'vàng pro' in SN[k].lower(): has[cc].add(16)
  if b=='JUICY MILK': has[cc].add(17)
for c,ri,di,f in D['events']: fl[CC[c]]|=f
for r in B['routes']:
  for x in r['rows']:
    c=x[0]; v=q.get(c,0); f=fl.get(c,0)
    x[10]=round(v,2) if v else ''
    x[11]='' if x[3] not in ('D','E') else ('Đã mua' if f&8 else 'Chưa mua')
    x[12]='Đã mua' if f&1 else 'Chưa mua'; x[13]='Đã mua' if f&4 else 'Chưa mua'
    for k in (14,15,16,17): x[k]='Có' if k in has[c] else 'Chưa'
# CCTB · số lần (ngày) đạt ảnh AI trong tháng theo loại (tủ, CVS, Tea, AQF); KH có nhiều tài sản cùng loại lấy tài sản ít lần đạt nhất; KH không có CCTB loại đó để trống
M=B['month']; A=(D.get('ai') or {}).get(M); CT={}
for x in (D.get('cctb') or {}).get(M, []): CT[CC[x[0]]]=x[2:6]
if A:
  per=collections.defaultdict(list)
  for c,ri,t,qr,seg,mk in A['a']:
    per[(CC[c],0 if t==4 else t)].append(bin(mk).count('1'))
  for r in B['routes']:
    for x in r['rows']:
      ct=CT.get(x[0])
      for k,t in [(6,0),(7,1),(8,2),(9,3)]:
        x[k]=(min(per[(x[0],t)]) if per.get((x[0],t)) else 0) if ct and ct[t] else ''
  B['aiAsof']=str(A['asof']).zfill(2)+'/'+M[5:]
last=D['rawLast']['d'].get('BINH HONG') or D['dates'][-1]; B['asof']=last[8:10]+'/'+last[5:7]
json.dump(B,open(F,'w'),ensure_ascii=False,separators=(',',':'))
print('asof',B['asof'],'brands',BR)

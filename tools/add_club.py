# Tracking tiến độ Club Silver (xlsb, sheet "DS chi tiết") → DATA.club[M] = [[c, ri, loại hình, Mức 1 LRB-AQF, Mức 2 LRB, kênh]]
# Chỉ KH "Đã đký Bạc" (Tham gia tháng); KH đồng thời có trong DS VIP Tết/Titan tháng đó thì chỉ giữ bên VIP (bỏ khỏi Club)
import json, sys, pickle, collections
from pyxlsb import open_workbook
SRC, M = sys.argv[1], sys.argv[2]; APPLY = 'apply' in sys.argv; P='/home/claude/sdo-de.html'
s=open(P,encoding='utf8').read(); i=s.index('const DATA = '); j=s.index(';</script>',i); D=json.loads(s[i+13:j])
R=[]
with open_workbook(SRC) as wb:
  with wb.get_sheet('DS chi tiết') as ws:
    for k,r in enumerate(ws.rows()):
      v=[c.v for c in r]
      if k>=7 and v[6] and str(v[12]).startswith('Tháng') and v[17]: R.append(v)
CC={c:k for k,c in enumerate(D['custCodes'])}; RI={r['code']:k for k,r in enumerate(D['routes'])}
TT={x[0] for x in (D.get('titan') or {}).get(M,[])}
rows=[]; bad=[]; newc=0; inT=[]
for v in R:
  kh=str(v[6]).strip().upper(); rt=str(v[5]).strip()
  if rt not in RI: bad.append((kh,rt)); continue
  if kh not in CC: CC[kh]=len(D['custCodes']); D['custCodes'].append(kh); D['custInfo'].append([v[7] or '','',v[10] or '','','']); newc+=1
  c=CC[kh]
  if c in TT: inT.append(kh); continue
  rows.append([c,RI[rt],str(v[10] or ''),float(v[18] or 0),float(v[17] or 0),str(v[16] or '')])
old={(D['custCodes'][x[0]],D['routes'][x[1]]['code']):x for x in D['club'].get(M,[])}
new={(D['custCodes'][x[0]],D['routes'][x[1]]['code']):x for x in rows}
NPP=lambda k: D['routes'][RI[k[1]]]['npp']
add=[k for k in new if k not in old]; rem=[k for k in old if k not in new]; chg=[k for k in new if k in old and new[k][2:]!=old[k][2:]]
print('file rows',len(R),'bad routes',len(bad),bad[:5],'in VIP (bỏ)',len(inT),'new codes',newc)
print('cũ',len(old),'mới',len(new),'thêm',len(add),'bỏ',len(rem),'đổi mức',len(chg))
print('thêm theo NPP',dict(collections.Counter(NPP(k) for k in add))); print('bỏ theo NPP',dict(collections.Counter(NPP(k) for k in rem)))
print('chg sample',[(k,old[k][3:5],new[k][3:5]) for k in chg[:10]])
print('tổng Mức1/Mức2 cũ',sum(x[3] for x in old.values()),sum(x[4] for x in old.values()),'mới',sum(x[3] for x in rows),sum(x[4] for x in rows))
json.dump({'add':add,'rem':rem,'chg':[(k,old[k][3:5],new[k][3:5]) for k in chg]},open('club_diff.json','w'),ensure_ascii=False)
if APPLY:
  D['club'][M]=rows; s=s[:i]+'const DATA = '+json.dumps(D,ensure_ascii=False,separators=(',',':'))+s[j:]; open(P,'w',encoding='utf8').write(s); print('applied')

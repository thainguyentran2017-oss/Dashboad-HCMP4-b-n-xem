# Danh sách CCTB tháng (cột: ... Mã Route(3), Mã KH(6), Sub Route(8), Segment(11), Tủ lạnh(13), Kệ CVS(14), Kệ Trà(15), Kệ AQF(16)) → DATA.cctb[m] = [[c, ri, tủ, cvs, tea, aqf, seg, thứ]]
import openpyxl, json, re, sys, collections
SRC,M=sys.argv[1],sys.argv[2]; APPLY='apply' in sys.argv; P='/home/claude/sdo-de.html'
s=open(P,encoding='utf8').read(); i=s.index('const DATA = '); j=s.index(';</script>',i); D=json.loads(s[i+13:j])
CC={c:k for k,c in enumerate(D['custCodes'])}; RI={r['code']:k for k,r in enumerate(D['routes'])}
ws=openpyxl.load_workbook(SRC,read_only=True,data_only=True).worksheets[0]; R=list(ws.iter_rows(values_only=True))
n=lambda v: int(float(v)) if v not in (None,'') else 0
rows=[]; bad=collections.Counter()
for r in R[1:]:
  if not r[6]: continue
  kh=str(r[6]).strip(); rt=str(r[3]).strip()
  if rt not in RI: bad['route '+rt]+=1; continue
  if kh not in CC: bad['kh']+=1; continue
  q=[n(r[13]),n(r[14]),n(r[15]),n(r[16])]
  if not any(q): continue
  rows.append([CC[kh],RI[rt]]+q+[str(r[11] or '').strip(), ','.join(re.findall(r'\d',str(r[8] or '')))])
old=D['cctb'].get(M,[]); ok={(x[0],x[1]):x for x in old}; nk={(x[0],x[1]):x for x in rows}
f=lambda L:[len(L)]+[sum(x[k] for x in L) for k in range(2,6)]
print('bad',dict(bad)); print('cũ',f(old)); print('mới',f(rows))
print('thêm KH',len([k for k in nk if k not in ok]),'bớt',len([k for k in ok if k not in nk]),'đổi SL',sum(1 for k in nk if k in ok and nk[k][2:6]!=ok[k][2:6]))
NPP=lambda k: D['routes'][k[1]]['npp']; d=collections.defaultdict(lambda:[0,0,0,0])
for k,x in nk.items():
  for t in range(4): d[NPP(k)][t]+=x[2+t]
for k,x in ok.items():
  for t in range(4): d[NPP(k)][t]-=x[2+t]
print('chênh theo NPP (tủ,cvs,trà,aqf)',{k:v for k,v in d.items() if any(v)})
if APPLY:
  D['cctb'][M]=rows; s=s[:i]+'const DATA = '+json.dumps(D,ensure_ascii=False,separators=(',',':'))+s[j:]; open(P,'w',encoding='utf8').write(s); print('applied')

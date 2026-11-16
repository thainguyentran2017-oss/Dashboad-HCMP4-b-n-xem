# Báo cáo kết quả chụp ảnh AI (sheet DetailbyPicture) → DATA.ai[m] = {w, asof, a:[[c, ri, loại(0 tủ,1 CVS,2 Tea,3 AQF,4 Counter), mã tài sản, seg, mask ngày đạt (bit d-1)]]}
import openpyxl, json, sys, collections
SRC=sys.argv[1]; M=sys.argv[2]; P='/home/claude/sdo-de.html'; DRY='--dry' in sys.argv
s=open(P,encoding='utf8').read(); i=s.index('const DATA = '); j=s.index(';</script>',i); D=json.loads(s[i+13:j])
CC={c:k for k,c in enumerate(D['custCodes'])}; RI={r['code']:k for k,r in enumerate(D['routes'])}
TY=lambda p: 0 if ('Tulanh' in p or p=='A0000000003') else 1 if ('CVS' in p or p=='A0000000006') else 2 if ('KeTea' in p or p=='A0000000004') else 3 if ('KeAqua' in p or p=='A0000000005') else 4 if 'Counter' in p else -1
ws=openpyxl.load_workbook(SRC,read_only=True,data_only=True)['DetailbyPicture']
P2={}; asof=0; unk=collections.Counter()
for r in ws.iter_rows(min_row=5,values_only=True):
  if not isinstance(r[0],int) or f'{r[0]}-{r[1]:02d}'!=M: continue
  ri=RI.get(r[9]); t=TY(str(r[17]))
  if ri is None or t<0: unk[(r[9],r[17])]+=1; continue
  kh=str(r[12]).strip(); c=CC.get(kh)
  if c is None: CC[kh]=c=len(D['custCodes']); D['custCodes'].append(kh); D['custInfo'].append([r[13] or '',r[14] or '',r[15] or '',r[16] or '',''])
  k=(ri,t,str(r[20])); o=P2.setdefault(k,[c,ri,t,str(r[20]),r[16],0])
  d=r[22].day; asof=max(asof,d)
  if r[24]=='Đạt': o[5]|=1<<(d-1)
old=D['ai'].get(M,{})
A={'w':old.get('w'),'asof':asof,'a':list(P2.values())}
print('AI',M,'tài sản',len(A['a']),'asof',asof,'unknown',dict(unk))
if DRY: json.dump(A,open('ai_dry.json','w'),ensure_ascii=False); sys.exit()
for kk,v in old.items():
  if kk not in A: A[kk]=v
D['ai'][M]=A
s=s[:i]+'const DATA = '+json.dumps(D,ensure_ascii=False,separators=(',',':'))+s[j:]
open(P,'w',encoding='utf8').write(s); print('applied')

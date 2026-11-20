# Chỉ tiêu số KH Trưng bày Tết theo tuyến (file chỉ tiêu: Route Code (1), TARGET) → DATA.tb.tgt = {mã route: số KH}
import openpyxl, json, sys
SRC=sys.argv[1]; P='/home/claude/sdo-de.html'
s=open(P,encoding='utf8').read(); i=s.index('const DATA = '); j=s.index(';</script>',i); D=json.loads(s[i+13:j])
RI={r['code'] for r in D['routes']}
ws=openpyxl.load_workbook(SRC,read_only=True,data_only=True).worksheets[0]; R=list(ws.iter_rows(values_only=True)); h=list(R[0])
ci=h.index('Route Code (1)'); ct=h.index('TARGET'); T={}
for r in R[1:]:
  if r[ci]: T[str(r[ci]).strip()]=int(r[ct] or 0)
bad=[k for k in T if k not in RI]; print('routes',len(T),'tổng',sum(T.values()),'không có trên dashboard',bad)
old=D['tb'].get('tgt'); D['tb']['tgt']=T; print('cũ', sum(old.values()) if old else None)
s=s[:i]+'const DATA = '+json.dumps(D,ensure_ascii=False,separators=(',',':'))+s[j:]; open(P,'w',encoding='utf8').write(s)

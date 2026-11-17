import pandas as pd,sys,json,collections
SRC=sys.argv[1]; M=sys.argv[2]; APPLY=len(sys.argv)>3; P='/home/claude/sdo-de.html'
d=pd.read_excel(SRC,sheet_name='By ASO',header=None,skiprows=6,dtype=str)
d.columns=['k','gws','grp','ss','npp','rt','kh','name','lh','note','sd','hl','h1','h2','ct','t1','t2']
d=d[(d.grp=='HCMP4')&d.ct.notna()]
s=open(P).read();i=s.index('const DATA = ');j=s.index(';</script>',i);D=json.loads(s[i+13:j])
R=D['routes'];RI={r['code']:k for k,r in enumerate(R)};CC={c:k for k,c in enumerate(D['custCodes'])}
f=lambda v: float(v) if isinstance(v,str) and v.strip() not in('','nan') else 0
oldL=D['titan'][M]; old={x[0]:x for x in oldL}
rp=set(RI[r] for r in d.rt)|{k for k,r in enumerate(R) if r['code'][3:5]=='RP'}
keep=[x for x in oldL if x[1] not in rp]
rows=[]
for _,r in d.iterrows():
  c=CC[r.kh]; t1,t2=f(r.t1),f(r.t2); ok=1 if r.sd=='1' else 0
  note=[]
  if r.note!='Hitlist': note.append('Ngoài Hitlist')
  if not t1: note.append('Chưa đăng ký LRB-AQF')
  if not ok: note.append('SD chưa duyệt')
  rows.append([c,RI[r.rt],r.lh,t1,t2,0,0,ok,' · '.join(note),'Đã duyệt' if ok else 'Chờ duyệt'])
rem=[x for x in oldL if x[1] in rp and x[0] not in {y[0] for y in rows}]
print('keep WS',len(keep),'retail new',len(rows),'removed',[(D['custCodes'][x[0]],R[x[1]]['code'],x[3],x[4],x[9]) for x in rem])
print('sd0',[(D['custCodes'][x[0]],R[x[1]]['npp']) for x in rows if not x[7]])
def agg(L): 
  c=collections.defaultdict(lambda:[0,0,0]);
  for x in L: n=R[x[1]]['npp']; c[n][0]+=1;c[n][1]+=x[3];c[n][2]+=x[4]
  return c
a=agg([x for x in oldL if x[1] in rp]); b=agg(rows)
for n in sorted(b,key=lambda n:-b[n][0]): print(n,a[n],b[n])
if APPLY:
  D['titan'][M]=keep+rows
  s=s[:i]+'const DATA = '+json.dumps(D,ensure_ascii=False,separators=(',',':'))+s[j:]; open(P,'w').write(s); print('applied',len(keep+rows))

# Nạp Rawdata 2025 (xlsx từng NPP) vào DATA.prev[m] (data/p{m}.js): tháng chưa có file p thì dựng từ khung trống
import json, subprocess, sys, os, re, copy, unicodedata
from python_calamine import CalamineWorkbook
S=os.path.dirname(os.path.abspath(__file__)); MAIN='/home/claude/sdo-de.html'; DD='/home/claude/data'; OUT=S+'/bp25'
def loadD(p):
  s=open(p,encoding='utf8').read(); i=s.index('const DATA = '); j=s.index(';</script>',i); return s,i,j,json.loads(s[i+13:j])
def loadP(m):
  f=f'{DD}/p{m}.js'
  if os.path.exists(f): t=open(f,encoding='utf8').read(); k=t.index('=')+1; return json.loads(t[k:].rstrip().rstrip(';'))
  t=open(f'{DD}/p2025-09.js',encoding='utf8').read(); k=t.index('=')+1; P=json.loads(t[k:].rstrip().rstrip(';'))
  for a in ['ev','skuEv','promo','vol','ord','nw','ordx','aqua','on','days','npps']: P[a]=[]
  P['rows']=0; P['m']=m; return P
s,i,j,D=loadD(MAIN)
bym={}
for f in sys.argv[1:]:
  R=CalamineWorkbook.from_path(f).get_sheet_by_index(0).to_python(nrows=50); H=[unicodedata.normalize('NFC',str(x)).strip() for x in R[0]]
  di=H.index('Ngày (Đơn Hàng)'); ni=H.index('Tên NPP'); m=next(str(r[di])[:7] for r in R[1:] if r[ni]); bym.setdefault(m,[]).append(f)
G=['custCodes','custInfo','skuNames','skuBrand','skuCat','skuGrp','custOnK','custB2B']
for m in sorted(bym):
  P=loadP(m); W=copy.deepcopy(D)
  W.update({'events':P['ev'],'skuEv':P['skuEv'],'promo':P.get('promo',[]),'vol':P['vol'],'ord':P['ord'],'nw':P['nw'],'ordx':P.get('ordx',[]),'aqua':P.get('aqua',[]),'custOn':P.get('on',[]),
            'dates':[m+'-01'],'dePk':[],'deMiss':[],'tg':[],'dh':[],'rawLast':{'d':{}},'updated':m+'-01'})
  tmp=f'{OUT}/t{m}.html'; open(tmp,'w',encoding='utf8').write(s[:i]+'const DATA = '+json.dumps(W,ensure_ascii=False,separators=(',',':'))+s[j:])
  rows=0
  for f in bym[m]:
    r=subprocess.run(['python3','-I',f'{S}/rb/splice.py',f,'auto',tmp],capture_output=True,text=True); out=r.stdout+r.stderr
    if r.returncode: print(out[-2000:]); sys.exit('splice lỗi '+f)
    print(m, re.search(r'NPP .*? rows \d+',out).group(0), re.findall(r'SKU mới.*',out)[:6]); rows+=int(re.search(r'rows (\d+)',out).group(1))
  _,_,_,T=loadD(tmp)
  for k in G: D[k]=T[k]
  di=sorted({x[2] for x in T['skuEv']}|{x[1] for x in T['vol']})
  RN={k:r['npp'] for k,r in enumerate(T['routes'])}
  P.update({'ev':T['events'],'skuEv':T['skuEv'],'promo':sorted(set(T['promo'])),'vol':T['vol'],'ord':T['ord'],'nw':T['nw'],'ordx':T['ordx'],'aqua':T['aqua'],'on':T['custOn'],
            'rows':(P.get('rows') or 0)+rows,'days':di,'npps':sorted({RN[x[0]] for x in T['vol']})})
  open(f'{OUT}/p{m}.js','w',encoding='utf8').write(f'DATA.prev["{m}"]='+json.dumps(P,ensure_ascii=False,separators=(',',':'))+';\n')
  print(m,'npps',P['npps'],'days',len(di),'size',os.path.getsize(f'{OUT}/p{m}.js'))
open(MAIN,'w',encoding='utf8').write(s[:i]+'const DATA = '+json.dumps(D,ensure_ascii=False,separators=(',',':'))+s[j:]); print('main globals updated', len(D['custCodes']), len(D['skuNames']))

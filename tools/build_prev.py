# Nạp Rawdata tháng cũ (CSV từng NPP) vào DATA.prev[m] (file data/p{m}.js) bằng splice.py trên bản HTML tạm
import json, subprocess, sys, os, re, glob, unicodedata, pandas as pd
S=os.path.dirname(os.path.abspath(__file__)); MAIN='/home/claude/sdo-de.html'; REPO='/home/claude/dashboad-hcmp4-b-n-xem/data'
files=sys.argv[1:]
def loadD(p):
  s=open(p,encoding='utf8').read(); i=s.index('const DATA = '); j=s.index(';</script>',i); return s,i,j,json.loads(s[i+13:j])
def loadP(m):
  f=f'{REPO}/p{m}.js'; t=open(f,encoding='utf8').read(); k=t.index('=')+1; return json.loads(t[k:].rstrip().rstrip(';'))
s,i,j,D=loadD(MAIN)
bym={}
for f in files:
  d=pd.read_csv(f,dtype=str,encoding='utf-8-sig',nrows=50); d.columns=[unicodedata.normalize('NFC',c) for c in d.columns]
  v=str(d['Ngày (Đơn Hàng)'].dropna().iloc[0]); import datetime
  t=datetime.datetime(1899,12,30)+datetime.timedelta(days=int(float(v))) if re.fullmatch(r'\d+(\.\d+)?',v) else datetime.datetime.strptime(v.split(' ')[0],'%m/%d/%Y')
  bym.setdefault(t.strftime('%Y-%m'),[]).append(f)
G=['custCodes','custInfo','skuNames','skuBrand','skuCat','skuGrp','custOnK','custB2B']
for m in sorted(bym):
  P=loadP(m); W=json.loads(json.dumps(D))
  W.update({'events':P['ev'],'skuEv':P['skuEv'],'promo':P.get('promo',[]),'vol':P['vol'],'ord':P['ord'],'nw':P['nw'],'ordx':P.get('ordx',[]),'aqua':P.get('aqua',[]),'custOn':P.get('on',[]),
            'dates':[m+'-01'],'dePk':[],'deMiss':[],'tg':[],'dh':[],'rawLast':{'d':{}},'updated':m+'-01'})
  tmp=f'{S}/bp/t{m}.html'; open(tmp,'w',encoding='utf8').write(s[:i]+'const DATA = '+json.dumps(W,ensure_ascii=False,separators=(',',':'))+s[j:])
  rows=0
  for f in bym[m]:
    r=subprocess.run(['python3','-I',f'{S}/rb/splice.py',f,'auto',tmp],capture_output=True,text=True); out=r.stdout+r.stderr
    if r.returncode: print(out); sys.exit('splice lỗi '+f)
    print(m, re.search(r'NPP .*? rows \d+',out).group(0), (re.findall(r'SKU mới.*',out) or [''])[0]); rows+=int(re.search(r'rows (\d+)',out).group(1))
  _,_,_,T=loadD(tmp)
  for k in G: D[k]=T[k]
  di=sorted({x[2] for x in T['skuEv']}|{x[1] for x in T['vol']})
  RN={k:r['npp'] for k,r in enumerate(T['routes'])}
  P.update({'ev':T['events'],'skuEv':T['skuEv'],'promo':sorted(set(T['promo'])),'vol':T['vol'],'ord':T['ord'],'nw':T['nw'],'ordx':T['ordx'],'aqua':T['aqua'],'on':T['custOn'],
            'rows':(P.get('rows') or 0)+rows,'days':di,'npps':sorted({RN[x[0]] for x in T['vol']})})
  open(f'{S}/bp/p{m}.js','w',encoding='utf8').write(f'DATA.prev["{m}"]='+json.dumps(P,ensure_ascii=False,separators=(',',':'))+';\n')
  print(m,'npps',P['npps'],'days',len(di),'size',os.path.getsize(f'{S}/bp/p{m}.js'))
open(MAIN,'w',encoding='utf8').write(s[:i]+'const DATA = '+json.dumps(D,ensure_ascii=False,separators=(',',':'))+s[j:]); print('main globals updated', len(D['custCodes']), len(D['skuNames']))

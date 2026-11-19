# Build the view-only copy (/home/claude/sdo-de-share.html) from the main dashboard (/home/claude/sdo-de.html)
import re, json, gzip, base64, sys, os
H=os.path.dirname(os.path.abspath(__file__))
SRC=sys.argv[1] if len(sys.argv)>1 else '/home/claude/sdo-de.html'; OUT=sys.argv[2] if len(sys.argv)>2 else '/home/claude/sdo-de-share.html'
ids=['tbNXls','tbNMsg','tbXls','tbMsg','tbLXls','tbLMsg','a5Xls','a5Msg','a5LXls','a5LMsg','gLXls','gLMsg','c3Xls','c3Msg','ttXls','ttMsg','eLXls','eLMsg','sLCsv','dLCsv','kLCsv','aLXls','tLXls','lLXls','sExport','kExport','kTXls','rLXls','rLMsg','ktXls','ktMsg','ckvXls','ckvMsg','bhXls','bhMsg','acXls','acMsg','invXls','invMsg','nChartExport','sChartExport','dChartExport','kChartExport','aLMsg','tLMsg','lLMsg','sExpMsg','kExpMsg','rTtXls','rTtMsg','rVXls','rVMsg','bhkXls','nkXls','uXls','uMsg']
LOG_URL="https://script.google.com/macros/s/AKfycbxjaDGoUyeiNEtmWPvxLbzUygTUUvOq_KhR005LwWNg-j33U1GQyVnKbM9v2bhvtkex/exec"
s=open(SRC,encoding='utf8').read()
def rep(a,b,n=1):
  global s
  if s.count(a)!=n: sys.exit('make_share: pattern count %d != %d: %r'%(s.count(a),n,a[:80]))
  s=s.replace(a,b)
s=s.replace('[hidden]:not([hidden=until-found i]){display:none!important}</style></head><body>','[hidden]:not([hidden=until-found i]){display:none!important}\n</style></head><body>',1)
s=re.sub(r'<!--MAIN-ONLY-->.*?<!--/MAIN-ONLY-->','',s,flags=re.S)
s=re.sub(r'/\*VW-MAIN\*/.*?/\*VW-MAIN-END\*/','',s,flags=re.S)
css=','.join('#'+i for i in ids)+'{display:none!important}#kload{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;background:var(--bg);color:var(--ink2);font-size:15px;z-index:99}'
rep('<title>Dashboard Tracking HCMP4</title>\n<style>\n','<title>Dashboard HCMP4 Bản xem</title>\n<style>\n'+css+'\n')
rep("const ACC_OWNER = true;","const ACC_OWNER = false;")
rep("const VIEW_GATE = false; ","const VIEW_GATE = true; ")
rep("const VIEW_LOG_URL = '';","const VIEW_LOG_URL = "+json.dumps(LOG_URL)+";")
rep("(async () => { try { dl = await window.claude?.use?.('downloads'); } catch(e){ dl = null; } dlReady = true; })();","dlReady = true; // view-only copy: no downloads")
i=s.index('<script>\nconst DATA = '); j=s.index('\n',i+9); line=s[i+9:j]
k=line.index(';</script>'); D=json.loads(line[13:k]); D.pop('inv',None)
_kt='/home/claude/data/klrt2026-10.js'  # KLR T10 chi tiết viếng thăm tách ra file riêng ở bản chính → gộp lại cho bản xem
if os.path.exists(_kt) and '2026-10' in D.get('klr',{}) and 't' not in D['klr']['2026-10']:
  _t=open(_kt,encoding='utf8').read(); D['klr']['2026-10']['t']=json.loads(_t[_t.index('=')+1:].rstrip().rstrip(';'))
assert line.endswith('<script>'), line[-80:]
gz=lambda t: base64.b64encode(gzip.compress(t.encode('utf8'),9)).decode()
ext=open(os.path.join(H,'ext_old.js'),encoding='utf8').read()
s=s[:i]+'<div id="kload">Đang mở dashboard…</div>\n<script>\nconst DATA_GZ = "'+gz(json.dumps(D,ensure_ascii=False,separators=(',',':')))+'";\nconst EXT_GZ = "'+gz(ext)+'";\n</script>\n<script type="text/plain" id="appsrc">\n'+s[j+1:]
tail=open(os.path.join(H,'loader_tail.txt'),encoding='utf8').read()
e=s.rindex('</script>'); s=s[:e]+'</script>\n'+tail
open(OUT,'w',encoding='utf8').write(s); print('share',OUT,len(s))

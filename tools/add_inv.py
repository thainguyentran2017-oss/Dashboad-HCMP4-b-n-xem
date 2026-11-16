# Báo cáo theo dõi tồn kho NPP (xlsx) → DATA.inv[npp] = {day, rows:[[nhãn, tên SP, quy cách, tồn (thùng), sku idx, FiF, mã SP]]}
import openpyxl, json, re, sys, collections
SRC=sys.argv[1]; P=sys.argv[2] if len(sys.argv)>2 else '/home/claude/sdo-de.html'; DRY='--dry' in sys.argv
ws=openpyxl.load_workbook(SRC,read_only=True,data_only=True).worksheets[0]; R=list(ws.iter_rows(values_only=True))
npp=None; day=None; wh=None; sec=None; items=collections.OrderedDict(); whs=collections.Counter()
for r in R:
  r=list(r)+[None]*20
  if r[0]=='Distributor : ': npp=str(r[5]).split(' - ',1)[1].strip()
  if r[0]=='Ngày:': day=str(r[5]).strip()
  if r[0] and str(r[0]).isupper() and r[1] is None and r[6] is None and '_' in str(r[0]): wh=str(r[0])
  if r[2] and r[6] is None and r[4] is None: sec=str(r[2])
  if r[6] and r[7] and r[4] and re.match(r'^\d+$',str(r[6])):
    whs[(wh,sec)]+=1
    if wh!='MAIN_WHS' or sec!='Product for Selling': continue
    nm=str(r[7]).strip(); m=re.search(r'x\s*(\d+)',nm,re.I) or re.search(r'-\s*(\d+)\s*chai',nm,re.I); per=int(m.group(1)) if m else 24
    c,u=(str(r[11]).replace(',','')+'/0').split('/')[:2]; v=float(c)+float(u or 0)/per
    fif=1 if re.search(r'^(Pepsi|7up|Mirinda)',nm,re.I) and re.search(r'1500',nm) else 0
    if fif: v/=2
    o=items.setdefault(nm,[str(r[4]).strip(),nm,0,0,fif,[]]); o[2]+=v; o[5].append(str(r[6]))
s=open(P,encoding='utf8').read(); i=s.index('const DATA = '); j=s.index(';</script>',i); D=json.loads(s[i+13:j])
SK={n:k for k,n in enumerate(D['skuNames'])}
def pk(nm):
  sz=re.search(r'(\d{3,4})\s*(?:x|-|ml)',nm,re.I); t='CAN' if re.search(r'\b(lon|can)\b',nm,re.I) else 'RGB' if re.search(r'thủy tinh',nm,re.I) else 'PET'
  return (sz.group(1)+'ml ' if sz else '')+t
rows=[[o[0],o[1],pk(o[1]),round(o[2],2),SK.get(o[1],-1),o[4],', '.join(o[5])] for o in items.values() if o[2] or o[1] in SK]
print('npp',npp,'day',day,'rows',len(rows),'warehouses',dict(whs),'tồn',round(sum(x[3] for x in rows),1))
if DRY: json.dump(rows,open('inv_dry.json','w'),ensure_ascii=False); sys.exit()
D.setdefault('inv',{})[npp]={'day':day,'rows':rows}
s=s[:i]+'const DATA = '+json.dumps(D,ensure_ascii=False,separators=(',',':'))+s[j:]
open(P,'w',encoding='utf8').write(s); print('applied')

# Báo cáo tiến độ đăng ký E-frame (sheet ASO Detail) → DATA.eframe = {m, k:{cidx:[trạng thái, số TK, ngân hàng, tên chủ TK, ngày ký]}}
import openpyxl, json, sys, collections
SRC,M=sys.argv[1],sys.argv[2]; APPLY='apply' in sys.argv; P='/home/claude/sdo-de.html'
s=open(P,encoding='utf8').read(); i=s.index('const DATA = '); j=s.index(';</script>',i); D=json.loads(s[i+13:j])
CC={c:k for k,c in enumerate(D['custCodes'])}
ws=openpyxl.load_workbook(SRC,read_only=True,data_only=True)['ASO Detail']
K={}; nrow=0; newc=0; dup=0
st=lambda v:'' if v is None else str(v).strip()
H5=[st(x) for x in next(ws.iter_rows(min_row=5,max_row=5,values_only=True))]; o=H5.index('Trạng thái')-11  # cột trạng thái có thể dời khi file thêm cột
for r in ws.iter_rows(min_row=6,values_only=True):
  kh=st(r[9]).upper()
  if not kh.startswith('CT'): continue
  nrow+=1
  if kh not in CC: CC[kh]=len(D['custCodes']); D['custCodes'].append(kh); D['custInfo'].append([st(r[10]),'','','','']); newc+=1
  c=str(CC[kh])
  if c in K:
    dup+=1
    if K[c][0]=='Hoàn thành ký': continue  # KH có 2 dòng (đang đổi TK): giữ dòng đã ký xong
  K[c]=[st(r[11+o]),st(r[15+o]),st(r[16+o]),st(r[13+o]),st(r[12+o])]
O=D.get('eframe',{}).get('k',{}); code=lambda c:D['custCodes'][int(c)]
print('rows',nrow,'KH',len(K),'dup',dup,'new codes',newc)
print('cũ',collections.Counter(v[0] for v in O.values())); print('mới',collections.Counter(v[0] for v in K.values()))
tr=collections.Counter((O[c][0] if c in O else '(không có)',K[c][0]) for c in K if c not in O or O[c][0]!=K[c][0])
tr.update(((O[c][0],'(bỏ khỏi file)') for c in O if c not in K)); print('chuyển trạng thái',dict(tr))
print('đổi thông tin TK (cùng trạng thái)',sum(1 for c in K if c in O and O[c][0]==K[c][0] and O[c][1:]!=K[c][1:]))
json.dump({'tr':[(code(c),O.get(c,[''])[0],K[c][0]) for c in K if c not in O or O[c][0]!=K[c][0]]+[(code(c),O[c][0],'(bỏ)') for c in O if c not in K]},open('ef_diff.json','w'),ensure_ascii=False)
if APPLY:
  D['eframe']={'m':M,'k':K}; s=s[:i]+'const DATA = '+json.dumps(D,ensure_ascii=False,separators=(',',':'))+s[j:]; open(P,'w',encoding='utf8').write(s); print('applied')

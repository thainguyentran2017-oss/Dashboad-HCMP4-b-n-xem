# Ghi ngày nhận file cho bảng "Tình trạng dữ liệu": python3 stamp_src.py key [YYYY-MM-DD]  (key: raw klr ai inv titan a5 eframe tb tbD cctb club)
import json,sys,datetime
P='/home/claude/sdo-de.html'; s=open(P,encoding='utf8').read(); i=s.index('const DATA = ')+13; j=s.index(';</script>',i); D=json.loads(s[i:j])
d=sys.argv[2] if len(sys.argv)>2 else (datetime.datetime.utcnow()+datetime.timedelta(hours=7)).strftime('%Y-%m-%d')
D.setdefault('src',{})[sys.argv[1]]=d
s=s[:i]+json.dumps(D,ensure_ascii=False,separators=(',',':'))+s[j:]; open(P,'w',encoding='utf8').write(s); print(sys.argv[1],d)

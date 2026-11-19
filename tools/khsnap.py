import json,sys
s=open(sys.argv[1],encoding='utf8').read(); i=s.index('const DATA = '); j=s.index(';</script>',i); D=json.loads(s[i+13:j])
json.dump({'rt':{r['code']:[r['npp'],[D['custCodes'][c] for c in r.get('kh',[])]] for r in D['routes']},'ci':{D['custCodes'][k]:v for k,v in enumerate(D['custInfo'])}},open(sys.argv[2],'w'),ensure_ascii=False)

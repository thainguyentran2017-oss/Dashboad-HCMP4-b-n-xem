import re, json
P='/home/claude/sdo-de.html'; s=open(P,encoding='utf8').read()
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt, (a[:80],n); s=s.replace(a,b)
# 1. remove CT AQF 500 tab button -> new tab button (both copies)
rep('    <!--MAIN-ONLY--><button type="button" role="tab" id="tab-aqf" aria-controls="view-aqf" aria-selected="false">CT AQF 500</button><!--/MAIN-ONLY-->\n',
    '    <button type="button" role="tab" id="tab-kb" aria-controls="view-kb" aria-selected="false">Trưng bày khối AQF</button>\n')
# 2. remove view-aqf markup
a=s.index('<!--MAIN-ONLY-->\n  <div class="view" id="view-aqf"'); b=s.index('<!--/MAIN-ONLY-->',a)+len('<!--/MAIN-ONLY-->\n'); s=s[:a]+s[b:]
# 3. remove AQF500/VIP Sales chốt JS block
a=s.index('/*VW-MAIN*/\n/* ---------- CT AQF 500:'); b=s.index('/*VW-MAIN-END*/',a)+len('/*VW-MAIN-END*/\n'); blk=s[a:b]; assert "$('vLoad').addEventListener('click', vipLoad);" in blk and blk.count('/*VW-MAIN')==2; s=s[:a]+s[b:]
# 4. lists
rep("ids: ['tt', 'a5', 'aqf', 'titan', 'club', 'c3', 'can']","ids: ['tt', 'a5', 'kb', 'titan', 'club', 'c3', 'can']")
rep("'tt','a5','sdo','aqf','de'","'tt','a5','kb','sdo','de'")
rep("  if (t === 'aqf') try { aqfRender(); } catch(e){ console.warn('aqf', e); }\n","  if (t === 'kb') try { kbRender(); } catch(e){ console.warn('kb', e); }\n")
rep("cv: u, ck: u, aqf: u,","cv: u, ck: u,")
rep("    ['CT AQF 500 (Google Sheet)', DATA.aqf && DATA.aqf.in ? `lấy lúc <b>${esc(DATA.aqf.in)}</b>` : '', '', ''],\n",
    "    ['DS Trưng bày khối AQF (DPM)', (DATA.kaqf || {}).rows ? `<b>${fmt(DATA.kaqf.rows.length)}</b> KH · <b>${mT(DATA.kaqf.m)}</b>` : '', S.kaqf, ''],\n")
rep(" if (!$('tab-aqf')) R2.splice(R2.findIndex(r => r[0].startsWith('CT AQF 500')), 1); // bản xem không có 2 mục này"," // bản xem không có mục Tồn kho")
rep('#tab-aqf{--tc:#0284c7}','#tab-kb{--tc:#0284c7}')
# 5. view markup after view-a5
VIEW='''  <div class="view" id="view-kb" role="tabpanel" aria-labelledby="tab-kb" hidden>
    <div class="filters" role="group" aria-label="Bộ lọc Trưng bày khối AQF">
      <div class="f"><label for="kbNpp">NPP</label><select id="kbNpp"></select></div>
      <div class="f"><label for="kbSs">SS</label><select id="kbSs"></select></div>
      <div class="f"><label for="kbRt">Tuyến</label><select id="kbRt"></select></div>
      <div class="f"><label for="kbLv">Mức</label><select id="kbLv"></select></div>
      <button class="reset" id="kbReset" type="button">Xóa lọc</button>
      <div class="pace" id="kbPace"></div>
    </div>
    <section class="panel" aria-labelledby="hKb" data-open="1">
      <div class="ktiles" id="kbKpis"></div>
      <div class="ph"><h2 id="hKb">Tracking Trưng bày khối AQF</h2><div class="exp"><button type="button" class="reset" id="kbBack" hidden>← Trở lại</button><button type="button" class="xbtn" id="kbXls">Tải Excel</button><span id="kbMsg" class="sub"></span></div></div>
      <div class="sub" id="kbNote"></div>
      <div class="vipm" id="kbSBox"><div class="ph vph"><h3>Tổng hợp theo NPP / SS / Tuyến</h3></div>
      <div class="seg" role="group" aria-label="Tổng hợp theo" id="kbBy" style="margin:6px 0"><button type="button" data-by="npp" aria-pressed="true">Theo NPP</button><button type="button" data-by="ss" aria-pressed="false">Theo SS</button><button type="button" data-by="rt" aria-pressed="false">Theo tuyến</button></div>
      <div class="tqf" id="kbF"></div>
      <div class="tw"><table class="rtab aqft a5t" id="kbTable"></table></div>
      </div>
      <div id="kbLBox" class="vipm">
        <div class="ph vph"><h3 id="hKbL">Danh sách khách hàng tham gia</h3><div class="exp"><input type="search" id="kbQ" placeholder="Tìm mã KH, tên KH, tuyến, NV…" style="min-width:220px"><button type="button" class="xbtn" id="kbLXls">Tải Excel</button><span id="kbLMsg" class="sub"></span></div></div>
        <div class="tqf" id="kbLF"></div>
        <div class="tw"><table class="rtab aqft a5t" id="kbLTable"></table></div>
      </div>
      <div id="kbNBox" class="vipm">
        <div class="ph vph"><h3 id="hKbN">KH không tham gia Tích luỹ AQF 500ml và chưa đăng ký Trưng bày khối AQF</h3><div class="exp"><input type="search" id="kbNQ" placeholder="Tìm mã KH, tên KH, tuyến, NV…" style="min-width:220px"><button type="button" class="xbtn" id="kbNXls">Tải Excel</button><span id="kbNMsg" class="sub"></span></div></div>
        <p class="sub" id="kbNNote"></p>
        <div class="tqf" id="kbNF"></div>
        <div class="tw"><table class="rtab aqft a5t" id="kbNTable"></table></div>
        <div><button type="button" class="reset" id="kbNMore" hidden>Xem thêm</button></div>
      </div>
    </section>
  </div>

'''
rep('  <div class="view" id="view-sdo" role="tabpanel"', VIEW+'  <div class="view" id="view-sdo" role="tabpanel"')
JS=open('/tmp/claude-0/-home-claude/feaff29c-22d9-57cb-984e-c6d87f84533b/scratchpad/kb.js',encoding='utf8').read()
rep('\n/* ---------- Cần chú ý hôm nay:', '\n'+JS+'\n/* ---------- Cần chú ý hôm nay:')
# 6. drop DATA.aqf
i=s.index('const DATA = '); j=s.index(';</script>',i); D=json.loads(s[i+13:j]); D.pop('aqf',None)
s=s[:i]+'const DATA = '+json.dumps(D,ensure_ascii=False,separators=(',',':'))+s[j:]
open(P,'w',encoding='utf8').write(s); print('ok', s.count('aqfRender'), s.count('view-aqf'))

/**
 * CAM KẾT NGÀY · NPP BÌNH HỒNG
 * 1) Chạy hàm setup() một lần: đổ danh sách KH vào 6 file, tạo ô tích, cài tự lọc theo thứ và tự ghi giờ.
 * 2) Khi có số liệu mới: chạy hàm capNhatSoLieu() (giữ nguyên các ô NV đã tích).
 * Sáng (hoặc tối hôm trước) NV tích CAM KẾT, chiều NV tích KẾT QUẢ NGÀY. Tuần sau NV tích lại cam kết thì dòng đó tự xoá cam kết/kết quả cũ.
 * 22h mỗi ngày các dòng có cam kết trong ngày được lưu vào tab "Lịch sử".
 * Sang tháng mới (5h sáng ngày 1, hoặc khi chạy capNhatSoLieu): xoá trắng số liệu "Đã thực hiện" và các cam kết / kết quả của tháng trước
 * (cam kết đã điền trong tháng mới được giữ lại).
 * Từ T11/2026: SDO 1 = Revive, SDO 2 = Tea+ → nhóm bao phủ "Tea" đổi thành "Rockstar".
 * Nhật ký tích: mỗi lần NV tích / bỏ tích / nhập SL ở phần cam kết hoặc kết quả, 1 dòng được ghi vào file "Nhật ký tích · Cam kết ngày Bình Hồng"
 * (thời gian, tuyến, NV, KH, phần, mục, giá trị) để xem giờ NV tích từng mục trên dashboard.
 */
var LOG_ID = '1PiqUReCf9Fwfd6mG0dGr7ei2gpZl75TECCYDuEQPgbM';
var DATA_URL = 'https://raw.githubusercontent.com/thainguyentran2017-oss/Dashboad-HCMP4-b-n-xem/main/bh/data.json';
var SHEET = 'Danh sách';
var TZ = 'Asia/Ho_Chi_Minh';
var HEAD_ROWS = 3, FIRST = 4, NCOL = 45;          // dữ liệu bắt đầu ở dòng 4, 45 cột (A..AS)
var CK1 = 19, CK2 = 30, KQ1 = 31, KQ2 = 42;       // S..AD = cam kết (sáng), AE..AP = kết quả ngày (chiều)
var CBS = [[19, 4], [24, 7], [31, 4], [36, 7]];   // các khối ô tích
var COL_SL = 23, COL_SLKQ = 35;                   // W = SL cam kết, AI = SL đã lấy
var COL_DATE = 43, COL_KQT = 44, COL_NOTE = 45;   // AQ = Ngày cam kết, AR = Giờ trả KQ, AS = Ghi chú
var HIST = 'Lịch sử';
var BLANK = function () { var a = []; for (var i = 19; i <= NCOL; i++) a.push(''); return a; };
var GROUPS = [['THÔNG TIN KHÁCH HÀNG', 6, '#1f7a6b'], ['CCTB', 4, '#4a5a8c'], ['ĐÃ THỰC HIỆN', 8, '#0e7490'],
  ['CAM KẾT CCTB (sáng)', 4, '#b45309'], ['CAM KẾT THỰC HIỆN (sáng)', 8, '#c2410c'],
  ['KẾT QUẢ CCTB (chiều)', 4, '#15803d'], ['KẾT QUẢ THỰC HIỆN (chiều)', 8, '#166534'], ['THEO DÕI', 3, '#475569']];
var HEAD = ['Mã KH', 'Tên KH', 'Thứ', 'SEG', 'Loại hình', 'Loại', 'Tủ', 'CVS', 'Tea', 'AQF', 'SL MTD', 'DE', 'SDO 1', 'SDO 2',
  'Bao phủ Tea', 'Bao phủ Boss cà phê', 'Bao phủ Sting Vàng Pro', 'Bao phủ Sữa trái cây',
  'Tủ', 'CVS', 'Tea', 'AQF', 'SL cam kết (thùng)', 'DE', 'SDO 1', 'SDO 2', 'Tea', 'Boss cà phê', 'Sting Vàng Pro', 'Sữa trái cây',
  'Tủ', 'CVS', 'Tea', 'AQF', 'SL đã lấy (thùng)', 'DE', 'SDO 1', 'SDO 2', 'Tea', 'Boss cà phê', 'Sting Vàng Pro', 'Sữa trái cây',
  'Ngày cam kết', 'Giờ trả KQ', 'Ghi chú'];

function loadData_() {
  var d = JSON.parse(UrlFetchApp.fetch(DATA_URL + '?t=' + Date.now()).getContentText());
  var cur = Utilities.formatDate(new Date(), TZ, 'yyyy-MM');
  d.month = d.month || cur;
  // data.json chưa sang tháng hiện tại → để trống số liệu
  if (d.month < cur) { d.month = cur; d.asof = ''; d.aiAsof = ''; d.routes.forEach(function (r) { r.rows.forEach(function (x) { for (var i = 6; i < 18; i++) x[i] = ''; }); }); }
  d.f1 = d.f1 || (d.month >= '2026-11' ? 'Rockstar' : 'Tea');
  d_aiAsof_ = d.aiAsof || ''; d_f1_ = d.f1; d_month_ = d.month;
  return d;
}
var d_f1_ = 'Tea', d_month_ = '';
function head_() { var h = HEAD.slice(); h[14] = 'Bao phủ ' + d_f1_; h[26] = d_f1_; h[38] = d_f1_; return h; }
function mLabel_(m) { return 'T' + (+m.slice(5)) + '/' + m.slice(0, 4); }

function setup() {
  var d = loadData_();
  ScriptApp.getProjectTriggers().forEach(function (t) { ScriptApp.deleteTrigger(t); });
  d.routes.forEach(function (r) {
    var ss = SpreadsheetApp.openById(r.id);
    var sh = ss.getSheetByName(SHEET) || ss.getSheets()[0];
    sh.setName(SHEET); sh.clear(); sh.getDataRange().clearDataValidations();
    ss.getSheets().forEach(function (s) { if (s.getName() !== SHEET && s.getName() !== HIST) ss.deleteSheet(s); });
    buildHeader_(sh, r, d.asof);
    var rows = r.rows.map(function (x) { return x.concat(BLANK()); });
    PropertiesService.getScriptProperties().setProperty('month', d.month);
    if (sh.getMaxColumns() < NCOL) sh.insertColumnsAfter(sh.getMaxColumns(), NCOL - sh.getMaxColumns());
    if (rows.length) sh.getRange(FIRST, 1, rows.length, NCOL).setValues(rows);
    formatBody_(sh, rows.length);
    ScriptApp.newTrigger('onOpenFile').forSpreadsheet(ss).onOpen().create();
    ScriptApp.newTrigger('onEditFile').forSpreadsheet(ss).onEdit().create();
    filterToday_(ss);
  });
  ScriptApp.newTrigger('filterAll').timeBased().atHour(5).everyDays(1).inTimezone(TZ).create();
  ScriptApp.newTrigger('luuLichSu').timeBased().atHour(22).everyDays(1).inTimezone(TZ).create();
  Logger.log('Xong: ' + d.routes.length + ' file');
}

// cập nhật cột số liệu (A..R) theo Mã KH, giữ nguyên phần cam kết NV đã điền; thêm KH mới vào cuối
function capNhatSoLieu() {
  var d = loadData_();
  var t0 = Utilities.parseDate(d.month + '-01 00:00', TZ, 'yyyy-MM-dd HH:mm').getTime() - 12 * 3600000;
  d.routes.forEach(function (r) {
    var ss = SpreadsheetApp.openById(r.id), sh = ss.getSheetByName(SHEET);
    sh.showRows(1, sh.getMaxRows());
    var n = Math.max(0, sh.getLastRow() - HEAD_ROWS), old = n ? sh.getRange(FIRST, 1, n, NCOL).getValues() : [], keep = {};
    old.forEach(function (x) {
      var dt = x[COL_DATE - 1];
      // sang tháng mới: chỉ giữ cam kết điền trong tháng mới (hoặc từ trưa ngày cuối tháng trước cho tuyến đầu tháng), còn lại xoá trắng
      if (!(dt instanceof Date) || dt.getTime() < t0) return;
      keep[x[0]] = x.slice(18);
    });
    var rows = r.rows.map(function (x) { return x.concat(keep[x[0]] || BLANK()); });
    if (n) sh.getRange(FIRST, 1, n, NCOL).clearContent();
    buildHeader_(sh, r, d.asof);
    if (rows.length) sh.getRange(FIRST, 1, rows.length, NCOL).setValues(rows);
    formatBody_(sh, rows.length);
    filterToday_(ss);
  });
  PropertiesService.getScriptProperties().setProperty('month', d.month);
  Logger.log('Đã cập nhật ' + d.routes.length + ' file · ' + mLabel_(d.month) + (d.asof ? ' · số liệu đến ' + d.asof : ' · chưa có số liệu tháng'));
}

var d_aiAsof_ = '';
function buildHeader_(sh, r, asof) {
  sh.getRange(1, 1, HEAD_ROWS, NCOL).breakApart();
  // hàng 1: A:B = tên NV (luôn hiện khi kéo ngang), C:AF = tiêu đề
  sh.getRange(1, 1, 1, 2).merge().setValue(r.code + ' · ' + r.nv);
  sh.getRange(1, 3, 1, NCOL - 2).merge().setValue('DANH SÁCH KHÁCH HÀNG · NPP BÌNH HỒNG · ' + mLabel_(d_month_) + ' · ' + (asof ? 'số liệu đến ' + asof : 'chưa có số liệu tháng') + ' · chỉ hiện KH của thứ hôm nay');
  sh.getRange(1, 1, 1, NCOL).setBackground('#1f7a6b').setFontColor('#ffffff').setFontWeight('bold').setFontSize(12);
  // hàng 2: nhóm cột; nhóm đầu tách A:B | C:F để cố định được 2 cột
  var G = [['KHÁCH HÀNG', 2, '#1f7a6b'], ['THÔNG TIN KH', 4, '#1f7a6b']].concat(GROUPS.slice(1)), c = 1;
  G.forEach(function (g) {
    sh.getRange(2, c, 1, g[1]).merge().setValue(g[0]);
    sh.getRange(2, c, 2, g[1]).setBackground(g[2]).setFontColor('#ffffff').setFontWeight('bold').setHorizontalAlignment('center');
    c += g[1];
  });
  sh.getRange(2, 7).setValue('CCTB · số lần đạt ảnh AI' + ((d_aiAsof_ || asof) ? ' (đến ' + (d_aiAsof_ || asof) + ')' : ''));
  sh.getRange(2, 11).setValue('ĐÃ THỰC HIỆN' + (asof ? ' (đến ' + asof + ')' : ' · ' + mLabel_(d_month_)));
  sh.getRange(3, 1, 1, NCOL).setValues([head_()]).setWrap(true).setVerticalAlignment('middle').setFontSize(9);
  sh.setRowHeight(3, 46); sh.setFrozenRows(HEAD_ROWS); sh.setFrozenColumns(2);
  var W = [90, 190, 55, 40, 60, 45, 95, 95, 95, 95, 60, 65, 65, 65, 65, 75, 80, 80, 40, 40, 40, 40, 70, 40, 45, 45, 40, 55, 60, 60,
    40, 40, 40, 40, 70, 40, 45, 45, 40, 55, 60, 60, 115, 115, 160];
  if (sh.getMaxColumns() < NCOL) sh.insertColumnsAfter(sh.getMaxColumns(), NCOL - sh.getMaxColumns());
  W.forEach(function (w, i) { sh.setColumnWidth(i + 1, w); });
}

function formatBody_(sh, n) {
  if (!n) return;
  var all = sh.getRange(FIRST, 1, n, NCOL);
  all.setFontSize(10).setBorder(true, true, true, true, true, true, '#d3dce8', SpreadsheetApp.BorderStyle.SOLID).setVerticalAlignment('middle');
  sh.getRange(FIRST, 2, n, 1).setFontWeight('bold');
  sh.getRange(FIRST, 3, n, 16).setHorizontalAlignment('center');
  sh.getRange(FIRST, 7, n, 4).setNumberFormat('0" lần"');
  sh.getRange(FIRST, CK1, n, 12).setBackground('#fffbeb').setHorizontalAlignment('center');
  sh.getRange(FIRST, KQ1, n, 12).setBackground('#f0fdf4').setHorizontalAlignment('center');
  CBS.forEach(function (p) { sh.getRange(FIRST, p[0], n, p[1]).insertCheckboxes(); });
  [COL_SL, COL_SLKQ].forEach(function (c) { sh.getRange(FIRST, c, n, 1).setDataValidation(SpreadsheetApp.newDataValidation().requireNumberGreaterThanOrEqualTo(0).setAllowInvalid(false).build()); });
  sh.getRange(FIRST, COL_DATE, n, 2).setNumberFormat('dd/MM/yyyy HH:mm').setFontColor('#64748b');
  // màu chữ: đạt / đã mua / có = xanh, chưa = đỏ
  var rules = [
    SpreadsheetApp.newConditionalFormatRule().whenTextStartsWith('Chưa').setFontColor('#b91c1c').setRanges([sh.getRange(FIRST, 11, n, 8)]).build(),
    SpreadsheetApp.newConditionalFormatRule().whenNumberEqualTo(0).setFontColor('#b91c1c').setRanges([sh.getRange(FIRST, 7, n, 4)]).build(),
    SpreadsheetApp.newConditionalFormatRule().whenNumberGreaterThan(0).setFontColor('#15803d').setBold(true).setRanges([sh.getRange(FIRST, 7, n, 4)]).build(),
    SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo('Đã mua').setFontColor('#15803d').setBold(true).setRanges([sh.getRange(FIRST, 12, n, 3)]).build(),
    SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo('Có').setFontColor('#15803d').setBold(true).setRanges([sh.getRange(FIRST, 15, n, 4)]).build()];
  sh.setConditionalFormatRules(rules);
  // chỉ cho NV sửa phần cam kết
  sh.getProtections(SpreadsheetApp.ProtectionType.SHEET).forEach(function (x) { x.remove(); });
  var p = sh.protect().setDescription('Chỉ sửa phần cam kết');
  p.setUnprotectedRanges([sh.getRange(FIRST, CK1, n, NCOL - CK1 + 1)]);
  p.setWarningOnly(true);
}

// chỉ hiện khách hàng của thứ hôm nay (T2..T7, CN)
function filterToday_(ss) {
  var sh = ss.getSheetByName(SHEET); if (!sh) return;
  var n = sh.getLastRow() - HEAD_ROWS; if (n <= 0) return;
  sh.showRows(FIRST, n);
  var u = +Utilities.formatDate(new Date(), TZ, 'u'), code = u === 7 ? 'CN' : 'T' + (u + 1);
  var v = sh.getRange(FIRST, 3, n, 1).getValues(), start = -1;
  for (var i = 0; i <= n; i++) {
    var hide = i < n && String(v[i][0]).split(',').map(function (s) { return s.trim(); }).indexOf(code) < 0;
    if (hide && start < 0) start = i;
    if (!hide && start >= 0) { sh.hideRows(FIRST + start, i - start); start = -1; }
  }
  sh.getRange(1, 3).setValue(String(sh.getRange(1, 3).getValue()).replace(/ · hôm nay .*$/, '') + ' · hôm nay ' + (code === 'CN' ? 'Chủ nhật' : 'Thứ ' + code.slice(1)));
}
// 5h sáng mỗi ngày: lọc KH theo thứ; ngày đầu tháng mới thì tự xoá trắng file
function filterAll() {
  var cur = Utilities.formatDate(new Date(), TZ, 'yyyy-MM');
  if (PropertiesService.getScriptProperties().getProperty('month') !== cur) { capNhatSoLieu(); return; }
  loadData_().routes.forEach(function (r) { try { filterToday_(SpreadsheetApp.openById(r.id)); } catch (e) {} });
}
function onOpenFile(e) { filterToday_(e.source); }

// Sáng: NV tích / nhập cam kết → ghi giờ cam kết; nếu dòng đang giữ cam kết của tuần trước thì xoá cam kết + kết quả cũ.
// Chiều: NV tích / nhập kết quả → ghi giờ trả kết quả.
// Sửa lỗi 05/11: trước đây hàm đọc cả dòng, ghi nhật ký (mở file khác, chờ khoá) rồi mới ghi đè lại CẢ DÒNG → nếu NV tích tiếp ô bên cạnh
// trong lúc chờ thì ô mới tích bị ghi đè mất (trông như tích "nhảy" sang ô khác). Nay: chỉ ghi đúng ô giờ (AQ / AR), chỉ xoá dòng cũ khi
// cam kết cũ đã quá 3 ngày, làm trong khoá ngắn, đọc lại dữ liệu mới nhất ngay trước khi ghi; nhật ký ghi SAU và không giữ khoá.
function onEditFile(e) {
  var rg = e.range, sh = rg.getSheet(); if (sh.getName() !== SHEET) return;
  var c1 = rg.getColumn(), c2 = rg.getLastColumn(), r = rg.getRow();
  if (r < FIRST || c2 < CK1 || c1 > KQ2) return;
  var now = new Date(), isCk = c1 <= CK2, n = rg.getNumRows();
  var lock = LockService.getScriptLock(); lock.waitLock(15000);
  try {
    var dates = sh.getRange(r, COL_DATE, n, 1).getValues();
    for (var k = 0; k < n; k++) {
      var row = r + k, dOld = dates[k][0];
      if (isCk) {
        // chỉ làm mới dòng khi cam kết cũ đã quá 3 ngày (tuần trước); dòng chưa có ngày thì không xoá gì
        if (dOld instanceof Date && now.getTime() - dOld.getTime() > 3 * 86400000) {
          var cur = sh.getRange(row, CK1, 1, COL_KQT - CK1 + 1).getValues()[0];
          for (var c = CK1; c < COL_DATE; c++) {
            if (c >= c1 && c <= c2) continue;                      // giữ ô NV vừa tích
            var blank = (c === COL_SL || c === COL_SLKQ) ? '' : false;
            if (cur[c - CK1] !== blank && cur[c - CK1] !== '') sh.getRange(row, c).setValue(blank);
          }
          sh.getRange(row, COL_KQT).setValue('');
        }
        sh.getRange(row, COL_DATE).setValue(now);
      } else {
        sh.getRange(row, COL_KQT).setValue(now);
      }
    }
    SpreadsheetApp.flush();
  } finally { lock.releaseLock(); }
  try { ghiNhatKy_(sh, rg, now); } catch (err) { Logger.log('nhat ky: ' + err); }
}

// ghi từng ô vừa sửa (trong phần cam kết / kết quả) vào file nhật ký chung (appendRow: không cần khoá, không chặn NV)
function ghiNhatKy_(sh, rg, now) {
  var a = Math.max(rg.getColumn(), CK1), b = Math.min(rg.getLastColumn(), KQ2); if (a > b) return;
  var n = rg.getNumRows(), r0 = rg.getRow();
  var head = sh.getRange(3, 1, 1, NCOL).getValues()[0], who = String(sh.getRange(1, 1).getValue() || ''), code = who.split(' · ')[0], nv = who.split(' · ').slice(1).join(' · ');
  var info = sh.getRange(r0, 1, n, 3).getValues(), vals = sh.getRange(r0, a, n, b - a + 1).getValues(), t = Utilities.formatDate(now, TZ, 'dd/MM/yyyy HH:mm:ss'), out = [];
  for (var i = 0; i < n; i++) {
    if (!/^CT/i.test(String(info[i][0]))) continue;
    for (var j = 0; j <= b - a; j++) {
      var c = a + j, v = vals[i][j], val = v === true ? 'Tích' : v === false ? 'Bỏ tích' : (v === '' || v == null ? 'Xoá' : v);
      out.push([t, code, nv, info[i][0], info[i][1], info[i][2], c <= CK2 ? 'Cam kết' : 'Kết quả', (c >= KQ1 && c <= KQ1 + 3 ? 'CCTB ' : c >= CK1 && c <= CK1 + 3 ? 'CCTB ' : '') + head[c - 1], val]);
    }
  }
  if (!out.length) return;
  var lg = SpreadsheetApp.openById(LOG_ID).getSheets()[0];
  out.forEach(function (x) { lg.appendRow(x); });
}

// 22h: lưu các dòng có cam kết trong ngày sang tab "Lịch sử" (giữ lịch sử khi tuần sau NV tích lại)
function luuLichSu() {
  loadData_().routes.forEach(function (r) {
    try {
      var ss = SpreadsheetApp.openById(r.id), sh = ss.getSheetByName(SHEET); if (!sh) return;
      var n = sh.getLastRow() - HEAD_ROWS; if (n <= 0) return;
      var today = Utilities.formatDate(new Date(), TZ, 'yyyyMMdd');
      var v = sh.getRange(FIRST, 1, n, NCOL).getValues().filter(function (x) {
        var d = x[COL_DATE - 1]; return d instanceof Date && Utilities.formatDate(d, TZ, 'yyyyMMdd') === today; });
      if (!v.length) return;
      var h = ss.getSheetByName(HIST);
      if (!h) { h = ss.insertSheet(HIST, ss.getSheets().length); h.appendRow(['Ngày lưu'].concat(sh.getRange(3, 1, 1, NCOL).getValues()[0])); h.setFrozenRows(1); h.hideSheet(); }
      var d = Utilities.formatDate(new Date(), TZ, 'dd/MM/yyyy');
      h.getRange(h.getLastRow() + 1, 1, v.length, NCOL + 1).setValues(v.map(function (x) { return [d].concat(x); }));
    } catch (e) {}
  });
}

// KHÔI PHỤC: lấy lại các ô cam kết / kết quả NV đã tích TRONG NGÀY HÔM NAY từ file Nhật ký tích (giá trị cuối cùng của từng ô).
// Dùng khi file bị xoá trắng (ví dụ lỡ chạy setup). Chạy bao nhiêu lần cũng được, không đụng các ngày khác.
function khoiPhucHomNay() {
  var d = loadData_(), today = Utilities.formatDate(new Date(), TZ, 'dd/MM/yyyy'), ids = {};
  d.routes.forEach(function (r) { ids[r.code] = r.id; });
  var lg = SpreadsheetApp.openById(LOG_ID).getSheets()[0], L = lg.getDataRange().getValues().slice(1);
  var ts = function (v) { return v instanceof Date ? v : Utilities.parseDate(String(v), TZ, 'dd/MM/yyyy HH:mm:ss'); };
  var day = function (v) { return v instanceof Date ? Utilities.formatDate(v, TZ, 'dd/MM/yyyy') : String(v).slice(0, 10); };
  var by = {};   // route → KH → {cells: {col: value}, ck: Date, kq: Date}
  var lab = {};  // 'Cam kết|mục' → cột
  var h = head_();
  for (var c = CK1; c <= KQ2; c++) lab[(c <= CK2 ? 'Cam kết' : 'Kết quả') + '|' + ((c >= KQ1 && c <= KQ1 + 3) || (c >= CK1 && c <= CK1 + 3) ? 'CCTB ' : '') + h[c - 1]] = c;
  L.filter(function (x) { return day(x[0]) === today; }).sort(function (a, b) { return ts(a[0]) - ts(b[0]); }).forEach(function (x) {
    var col = lab[x[6] + '|' + x[7]]; if (!col || !ids[x[1]]) return;
    var R = by[x[1]] = by[x[1]] || {}, K = R[x[3]] = R[x[3]] || {cells: {}, ck: null, kq: null}, t = ts(x[0]), v = x[8];
    K.cells[col] = v === 'Tích' ? true : v === 'Bỏ tích' ? false : v === 'Xoá' ? '' : v;
    if (col <= CK2) { if (!K.ck) K.ck = t; } else K.kq = t;
  });
  var nOk = 0;
  Object.keys(by).forEach(function (code) {
    var ss = SpreadsheetApp.openById(ids[code]), sh = ss.getSheetByName(SHEET), n = sh.getLastRow() - HEAD_ROWS; if (n <= 0) return;
    var keys = sh.getRange(FIRST, 1, n, 1).getValues(), rg = sh.getRange(FIRST, CK1, n, COL_KQT - CK1 + 1), v = rg.getValues();
    keys.forEach(function (k, i) {
      var K = by[code][k[0]]; if (!K) return;
      for (var col in K.cells) v[i][col - CK1] = K.cells[col];
      if (K.ck) v[i][COL_DATE - CK1] = K.ck;
      if (K.kq) v[i][COL_KQT - CK1] = K.kq;
      nOk++;
    });
    rg.setValues(v);
  });
  SpreadsheetApp.flush();
  Logger.log('Đã khôi phục ' + nOk + ' KH đã tích trong ngày ' + today);
}

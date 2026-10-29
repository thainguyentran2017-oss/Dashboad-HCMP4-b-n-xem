/**
 * CAM KẾT NGÀY · NPP BÌNH HỒNG
 * 1) Chạy hàm setup() một lần: đổ danh sách KH vào 6 file, tạo ô tích, cài tự lọc theo thứ và tự ghi giờ.
 * 2) Khi có số liệu mới: chạy hàm capNhatSoLieu() (giữ nguyên các ô NV đã tích).
 * Sáng NV tích CAM KẾT, chiều NV tích KẾT QUẢ NGÀY. Ngày mới NV tích lại cam kết thì dòng đó tự xoá cam kết/kết quả cũ.
 * 22h mỗi ngày các dòng có cam kết trong ngày được lưu vào tab "Lịch sử".
 */
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

function loadData_() { var d = JSON.parse(UrlFetchApp.fetch(DATA_URL + '?t=' + Date.now()).getContentText()); d_aiAsof_ = d.aiAsof || ''; return d; }

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
  d.routes.forEach(function (r) {
    var ss = SpreadsheetApp.openById(r.id), sh = ss.getSheetByName(SHEET);
    sh.showRows(1, sh.getMaxRows());
    var n = Math.max(0, sh.getLastRow() - HEAD_ROWS), old = n ? sh.getRange(FIRST, 1, n, NCOL).getValues() : [], keep = {};
    old.forEach(function (x) { keep[x[0]] = x.slice(18); });
    var rows = r.rows.map(function (x) { return x.concat(keep[x[0]] || BLANK()); });
    if (n) sh.getRange(FIRST, 1, n, NCOL).clearContent();
    buildHeader_(sh, r, d.asof);
    if (rows.length) sh.getRange(FIRST, 1, rows.length, NCOL).setValues(rows);
    formatBody_(sh, rows.length);
    filterToday_(ss);
  });
}

var d_aiAsof_ = '';
function buildHeader_(sh, r, asof) {
  sh.getRange(1, 1, HEAD_ROWS, NCOL).breakApart();
  // hàng 1: A:B = tên NV (luôn hiện khi kéo ngang), C:AF = tiêu đề
  sh.getRange(1, 1, 1, 2).merge().setValue(r.code + ' · ' + r.nv);
  sh.getRange(1, 3, 1, NCOL - 2).merge().setValue('DANH SÁCH KHÁCH HÀNG · NPP BÌNH HỒNG · số liệu đến ' + asof + ' · chỉ hiện KH của thứ hôm nay');
  sh.getRange(1, 1, 1, NCOL).setBackground('#1f7a6b').setFontColor('#ffffff').setFontWeight('bold').setFontSize(12);
  // hàng 2: nhóm cột; nhóm đầu tách A:B | C:F để cố định được 2 cột
  var G = [['KHÁCH HÀNG', 2, '#1f7a6b'], ['THÔNG TIN KH', 4, '#1f7a6b']].concat(GROUPS.slice(1)), c = 1;
  G.forEach(function (g) {
    sh.getRange(2, c, 1, g[1]).merge().setValue(g[0]);
    sh.getRange(2, c, 2, g[1]).setBackground(g[2]).setFontColor('#ffffff').setFontWeight('bold').setHorizontalAlignment('center');
    c += g[1];
  });
  sh.getRange(2, 7).setValue('CCTB · số lần đạt ảnh AI (đến ' + (d_aiAsof_ || asof) + ')');
  sh.getRange(2, 11).setValue('ĐÃ THỰC HIỆN (đến ' + asof + ')');
  sh.getRange(3, 1, 1, NCOL).setValues([HEAD]).setWrap(true).setVerticalAlignment('middle').setFontSize(9);
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
function filterAll() { loadData_().routes.forEach(function (r) { try { filterToday_(SpreadsheetApp.openById(r.id)); } catch (e) {} }); }
function onOpenFile(e) { filterToday_(e.source); }

// Sáng: NV tích / nhập cam kết → ghi giờ cam kết; nếu dòng đang giữ cam kết của ngày cũ thì xoá cam kết + kết quả cũ.
// Chiều: NV tích / nhập kết quả → ghi giờ trả kết quả.
function onEditFile(e) {
  var rg = e.range, sh = rg.getSheet(); if (sh.getName() !== SHEET) return;
  var c1 = rg.getColumn(), c2 = rg.getLastColumn(), r = rg.getRow();
  if (r < FIRST || c2 < CK1 || c1 > KQ2) return;
  var now = new Date(), today = Utilities.formatDate(now, TZ, 'yyyyMMdd');
  for (var k = 0; k < rg.getNumRows(); k++) {
    var row = r + k, cell = sh.getRange(row, CK1, 1, COL_KQT - CK1 + 1), v = cell.getValues()[0];
    var dOld = v[COL_DATE - CK1], isCk = c1 <= CK2;
    if (isCk) {
      if (!(dOld instanceof Date) || Utilities.formatDate(dOld, TZ, 'yyyyMMdd') !== today) {
        for (var c = CK1; c <= COL_KQT; c++) {
          if (c >= c1 && c <= c2) continue;
          v[c - CK1] = (c === COL_SL || c === COL_SLKQ || c >= COL_DATE) ? '' : false;
        }
      }
      v[COL_DATE - CK1] = now;
    } else {
      v[COL_KQT - CK1] = now;
    }
    cell.setValues([v]);
  }
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

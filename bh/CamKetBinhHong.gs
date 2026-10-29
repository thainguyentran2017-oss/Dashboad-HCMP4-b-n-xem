/**
 * CAM KẾT NGÀY · NPP BÌNH HỒNG
 * 1) Chạy hàm setup() một lần: đổ danh sách KH vào 6 file, tạo ô tích, cài tự lọc theo thứ và tự ghi ngày cam kết.
 * 2) Khi có số liệu mới: chạy hàm capNhatSoLieu() (giữ nguyên các ô NV đã tích).
 */
var DATA_URL = 'https://raw.githubusercontent.com/thainguyentran2017-oss/Dashboad-HCMP4-b-n-xem/main/bh/data.json';
var SHEET = 'Danh sách';
var TZ = 'Asia/Ho_Chi_Minh';
var HEAD_ROWS = 3, FIRST = 4, NCOL = 32;          // dữ liệu bắt đầu ở dòng 4, 32 cột (A..AF)
var COMMIT_CB = [[19, 4], [24, 7]];               // S..V và X..AD là ô tích
var COL_SL = 23, COL_DATE = 31, COL_NOTE = 32;    // W = SL cam kết, AE = Ngày cam kết, AF = Ghi chú
var GROUPS = [['THÔNG TIN KHÁCH HÀNG', 6, '#1f7a6b'], ['CCTB', 4, '#4a5a8c'], ['ĐÃ THỰC HIỆN', 8, '#0e7490'],
  ['CAM KẾT CCTB', 4, '#b45309'], ['CAM KẾT THỰC HIỆN', 8, '#c2410c'], ['THEO DÕI', 2, '#475569']];
var HEAD = ['Mã KH', 'Tên KH', 'Thứ', 'SEG', 'Loại hình', 'Loại', 'Tủ', 'CVS', 'Tea', 'AQF', 'SL MTD', 'DE', 'SDO 1', 'SDO 2',
  'Bao phủ Tea', 'Bao phủ Boss cà phê', 'Bao phủ Sting Vàng Pro', 'Bao phủ Sữa trái cây',
  'Tủ', 'CVS', 'Tea', 'AQF', 'SL cam kết (thùng)', 'DE', 'SDO 1', 'SDO 2', 'Tea', 'Boss cà phê', 'Sting Vàng Pro', 'Sữa trái cây', 'Ngày cam kết', 'Ghi chú'];

function loadData_() { return JSON.parse(UrlFetchApp.fetch(DATA_URL + '?t=' + Date.now()).getContentText()); }

function setup() {
  var d = loadData_();
  ScriptApp.getProjectTriggers().forEach(function (t) { ScriptApp.deleteTrigger(t); });
  d.routes.forEach(function (r) {
    var ss = SpreadsheetApp.openById(r.id);
    var sh = ss.getSheetByName(SHEET) || ss.getSheets()[0];
    sh.setName(SHEET); sh.clear(); sh.getDataRange().clearDataValidations();
    ss.getSheets().forEach(function (s) { if (s.getName() !== SHEET) ss.deleteSheet(s); });
    buildHeader_(sh, r, d.asof);
    var rows = r.rows.map(function (x) { return x.concat(['', '', '', '', '', '', '', '', '', '', '', '', '', '']); });
    if (sh.getMaxColumns() < NCOL) sh.insertColumnsAfter(sh.getMaxColumns(), NCOL - sh.getMaxColumns());
    if (rows.length) sh.getRange(FIRST, 1, rows.length, NCOL).setValues(rows);
    formatBody_(sh, rows.length);
    ScriptApp.newTrigger('onOpenFile').forSpreadsheet(ss).onOpen().create();
    ScriptApp.newTrigger('onEditFile').forSpreadsheet(ss).onEdit().create();
    filterToday_(ss);
  });
  ScriptApp.newTrigger('filterAll').timeBased().atHour(5).everyDays(1).inTimezone(TZ).create();
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
    var rows = r.rows.map(function (x) { return x.concat(keep[x[0]] || ['', '', '', '', '', '', '', '', '', '', '', '', '', '']); });
    if (n) sh.getRange(FIRST, 1, n, NCOL).clearContent();
    buildHeader_(sh, r, d.asof);
    if (rows.length) sh.getRange(FIRST, 1, rows.length, NCOL).setValues(rows);
    formatBody_(sh, rows.length);
    filterToday_(ss);
  });
}

function buildHeader_(sh, r, asof) {
  sh.getRange(1, 1, HEAD_ROWS, NCOL).breakApart();
  sh.getRange(1, 1, 1, NCOL).merge().setValue('DANH SÁCH KHÁCH HÀNG · ' + r.code + ' · ' + r.nv + ' · NPP BÌNH HỒNG · số liệu đến ' + asof + ' · chỉ hiện KH của thứ hôm nay')
    .setBackground('#1f7a6b').setFontColor('#ffffff').setFontWeight('bold').setFontSize(12);
  var c = 1;
  GROUPS.forEach(function (g) {
    sh.getRange(2, c, 1, g[1]).merge().setValue(g[0]);
    sh.getRange(2, c, 2, g[1]).setBackground(g[2]).setFontColor('#ffffff').setFontWeight('bold').setHorizontalAlignment('center');
    c += g[1];
  });
  sh.getRange(2, 7).setValue('CCTB (Đạt ảnh AI)');
  sh.getRange(2, 11).setValue('ĐÃ THỰC HIỆN (đến ' + asof + ')');
  sh.getRange(3, 1, 1, NCOL).setValues([HEAD]).setWrap(true).setVerticalAlignment('middle').setFontSize(9);
  sh.setRowHeight(3, 46); sh.setFrozenColumns(0); sh.setFrozenRows(HEAD_ROWS);
  var W = [90, 190, 55, 40, 60, 45, 95, 95, 95, 95, 60, 65, 65, 65, 65, 75, 80, 80, 40, 40, 40, 40, 70, 40, 45, 45, 40, 55, 60, 60, 115, 160];
  W.forEach(function (w, i) { sh.setColumnWidth(i + 1, w); });
}

function formatBody_(sh, n) {
  if (!n) return;
  var all = sh.getRange(FIRST, 1, n, NCOL);
  all.setFontSize(10).setBorder(true, true, true, true, true, true, '#d3dce8', SpreadsheetApp.BorderStyle.SOLID).setVerticalAlignment('middle');
  sh.getRange(FIRST, 2, n, 1).setFontWeight('bold');
  sh.getRange(FIRST, 3, n, 16).setHorizontalAlignment('center');
  sh.getRange(FIRST, 19, n, 12).setBackground('#fffbeb').setHorizontalAlignment('center');
  COMMIT_CB.forEach(function (p) { var rg = sh.getRange(FIRST, p[0], n, p[1]); rg.insertCheckboxes(); });
  sh.getRange(FIRST, COL_SL, n, 1).setDataValidation(SpreadsheetApp.newDataValidation().requireNumberGreaterThanOrEqualTo(0).setAllowInvalid(false).build());
  sh.getRange(FIRST, COL_DATE, n, 1).setNumberFormat('dd/MM/yyyy HH:mm').setFontColor('#64748b');
  // màu chữ: đạt / đã mua / có = xanh, chưa = đỏ
  var rules = [
    SpreadsheetApp.newConditionalFormatRule().whenTextStartsWith('Chưa').setFontColor('#b91c1c').setRanges([sh.getRange(FIRST, 7, n, 12)]).build(),
    SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo('Đạt AI').setFontColor('#15803d').setBold(true).setRanges([sh.getRange(FIRST, 7, n, 4)]).build(),
    SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo('Đã mua').setFontColor('#15803d').setBold(true).setRanges([sh.getRange(FIRST, 12, n, 3)]).build(),
    SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo('Có').setFontColor('#15803d').setBold(true).setRanges([sh.getRange(FIRST, 15, n, 4)]).build()];
  sh.setConditionalFormatRules(rules);
  // chỉ cho NV sửa phần cam kết
  sh.getProtections(SpreadsheetApp.ProtectionType.SHEET).forEach(function (x) { x.remove(); });
  var p = sh.protect().setDescription('Chỉ sửa phần cam kết');
  p.setUnprotectedRanges([sh.getRange(FIRST, 19, n, 14)]);
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
  sh.getRange(1, 1).setValue(String(sh.getRange(1, 1).getValue()).replace(/ · hôm nay .*$/, '') + ' · hôm nay ' + (code === 'CN' ? 'Chủ nhật' : 'Thứ ' + code.slice(1)));
}
function filterAll() { loadData_().routes.forEach(function (r) { try { filterToday_(SpreadsheetApp.openById(r.id)); } catch (e) {} }); }
function onOpenFile(e) { filterToday_(e.source); }

// NV tích / nhập cam kết → tự ghi ngày giờ cam kết của dòng đó
function onEditFile(e) {
  var rg = e.range, sh = rg.getSheet(); if (sh.getName() !== SHEET) return;
  var c = rg.getColumn(), r = rg.getRow();
  if (r < FIRST || c < 19 || c > 30) return;
  for (var k = 0; k < rg.getNumRows(); k++) sh.getRange(r + k, COL_DATE).setValue(new Date());
}

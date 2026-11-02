/**
 * CHỈ TIÊU AQF 500 THÁNG 11 & 12 · NPP BÌNH HỒNG (HCMP4)
 * Chạy hàm taoBang() MỘT LẦN để tạo 2 sheet: ASO (danh sách KH để NV điền) và ROUTE (tổng hợp theo tuyến).
 * Chạy lại taoBang() sẽ GIỮ NGUYÊN số NV đã điền ở 2 cột Nov'26 / Dec'26 (khớp theo Mã KH).
 */
var DATA_URL = 'https://raw.githubusercontent.com/thainguyentran2017-oss/Dashboad-HCMP4-b-n-xem/main/aqf/aso.json';

function onOpen() {
  SpreadsheetApp.getUi().createMenu('AQF 500').addItem('Tạo / làm mới bảng', 'taoBang').addToUi();
}

// Sheet tiếng Việt dùng dấu ";" ngăn cách đối số trong công thức → đổi "," thành ";" theo locale của file
var SEP_ = ',';
function F_(f) { return SEP_ === ',' ? f : f.replace(/,/g, SEP_); }

function taoBang() {
  var ss = SpreadsheetApp.getActive();
  var loc = String(ss.getSpreadsheetLocale() || '');
  SEP_ = /^(en|th|ja|ko|zh|he|ms|fil|hi)/.test(loc) || /_(US|GB|AU|CA|IN|IE|NZ|SG|PH|MY)$/.test(loc) && !/^(vi|fr|de|es|it|pt|ru|nl|pl|tr|id)/.test(loc) ? ',' : ';';
  var d = JSON.parse(UrlFetchApp.fetch(DATA_URL + '?t=' + Date.now()).getContentText());
  var rows = d.rows, n = rows.length, last = 3 + n;

  // giữ số NV đã điền
  var keep = {};
  var old = ss.getSheetByName('ASO');
  if (old && old.getLastRow() >= 4) {
    old.getRange(4, 1, old.getLastRow() - 3, 20).getValues().forEach(function (r) {
      if (r[7] && (r[17] !== '' || r[18] !== '' || r[19] !== '')) keep[r[7]] = [r[17], r[18], r[19]];
    });
  }

  var ws = old || ss.insertSheet('ASO');
  ws.clear(); ws.clearConditionalFormatRules();
  if (ws.getFilter()) ws.getFilter().remove();
  if (ws.getMaxColumns() < 21) ws.insertColumnsAfter(ws.getMaxColumns(), 21 - ws.getMaxColumns());
  if (ws.getMaxRows() < last + 2) ws.insertRowsAfter(ws.getMaxRows(), last + 2 - ws.getMaxRows());
  ws.getRange('A1:U3').breakApart();

  var H = ['Group', 'DisCode', 'DisName', 'SS', 'RouteCode', 'Tên NV', 'RouteType', 'OutletCode', 'OutletName', 'Loại hình',
    'MAX\n(2025-2026)', 'L3M', "YAGO\n(ave Nov-Dec'25)", "Nov'25", "Dec'25", 'Max L3M, YAGO\n>=25rc/ Tháng', 'TMKT ĐỀ NGHỊ', "Nov'26", "Dec'26", 'Ghi chú NV', 'Kiểm tra'];
  ws.getRange('A1').setValue('SET UP TARGET AQF 500 THÁNG 11 & 12 · NPP BÌNH HỒNG (HCMP4)').setFontSize(14).setFontWeight('bold').setFontColor('#0070C0');
  ws.getRange('K2:O2').merge().setValue('VOL HISTORICAL');
  ws.getRange('Q2').setValue('TARGET/ THÁNG');
  ws.getRange('R2:S2').merge().setValue('TARGET SALES INPUT (NV điền)');
  ws.getRange('K2:S2').setFontWeight('bold').setFontColor('#ffffff').setHorizontalAlignment('center');
  ws.getRange('K2:P2').setBackground('#0070C0'); ws.getRange('Q2').setBackground('#C00000'); ws.getRange('R2:S2').setBackground('#7030A0');
  ws.getRange(3, 1, 1, H.length).setValues([H]).setFontWeight('bold').setFontColor('#ffffff').setBackground('#0070C0')
    .setHorizontalAlignment('center').setVerticalAlignment('middle').setWrap(true);
  ws.getRange('Q3').setBackground('#C00000'); ws.getRange('R3:T3').setBackground('#7030A0');
  ws.setRowHeight(3, 48);

  var vals = rows.map(function (r, i) {
    var k = 4 + i, kp = keep[r[4]] || ['', '', ''];
    return ['HCMP4', d.disCode, d.npp, r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10], r[11], r[12], r[13], kp[0], kp[1], kp[2],
      F_('=IF(AND(R' + k + '="",S' + k + '=""),"",IF(OR(AND(R' + k + '<>"",R' + k + '<Q' + k + '),AND(S' + k + '<>"",S' + k + '<Q' + k + ')),"Cần trình SD phê duyệt","ok"))')];
  });
  ws.getRange(4, 1, n, 21).setValues(vals);
  ws.getRange(4, 11, n, 7).setNumberFormat('#,##0.#;-#,##0.#;""');
  ws.getRange(4, 18, n, 2).setNumberFormat('#,##0').setBackground('#FFF2CC');
  ws.getRange(4, 17, n, 1).setFontWeight('bold').setFontColor('#C00000');
  ws.getRange(3, 1, n + 1, 21).setBorder(true, true, true, true, true, true, '#BFBFBF', SpreadsheetApp.BorderStyle.SOLID);
  ['K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S'].forEach(function (c) {
    ws.getRange(c + '1').setFormula(F_('=SUBTOTAL(9,' + c + '4:' + c + last + ')')).setNumberFormat('#,##0').setFontWeight('bold');
  });
  // chỉ cho nhập số ≥ 0 ở 2 cột chỉ tiêu
  ws.getRange(4, 18, n, 2).setDataValidation(SpreadsheetApp.newDataValidation().requireNumberGreaterThanOrEqualTo(0)
    .setAllowInvalid(false).setHelpText('Nhập chỉ tiêu AQF 500 (thùng) của KH trong tháng').build());
  var rule = SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo('Cần trình SD phê duyệt').setBackground('#FDE2E2').setFontColor('#B91C1C')
    .setRanges([ws.getRange(4, 21, n, 1)]).build();
  var ok = SpreadsheetApp.newConditionalFormatRule().whenTextEqualTo('ok').setBackground('#DCFCE7').setFontColor('#15803D')
    .setRanges([ws.getRange(4, 21, n, 1)]).build();
  ws.setConditionalFormatRules([rule, ok]);
  [8, 10, 12, 18, 13, 20, 12, 13, 26, 9, 11, 9, 11, 8, 8, 13, 12, 11, 11, 22, 20].forEach(function (w, i) { ws.setColumnWidth(i + 1, w * 7.5); });
  ws.setFrozenRows(3); ws.setFrozenColumns(9);
  ws.getRange(3, 1, n + 1, 21).createFilter();

  // ROUTE
  var w2 = ss.getSheetByName('ROUTE') || ss.insertSheet('ROUTE');
  w2.clear();
  var codes = [], seen = {};
  rows.forEach(function (r) { if (!seen[r[1]]) { seen[r[1]] = r; codes.push(r[1]); } });
  var H2 = ['SS', 'Mã Route', 'Tên NV', 'Loại Route', 'RouteList', 'Hitlist', 'MAX', 'L3M', 'YAGO', "Nov'25", "Dec'25", 'TMKT ĐỀ NGHỊ', "Nov'26", "Dec'26", 'KH đã điền', 'KH cần trình SD'];
  w2.getRange('A1').setValue('TỔNG HỢP THEO TUYẾN · AQF 500 THÁNG 11 & 12 · BÌNH HỒNG').setFontSize(14).setFontWeight('bold').setFontColor('#0070C0');
  w2.getRange(3, 1, 1, H2.length).setValues([H2]).setFontWeight('bold').setFontColor('#ffffff').setBackground('#0070C0')
    .setHorizontalAlignment('center').setVerticalAlignment('middle').setWrap(true);
  w2.getRange('L3').setBackground('#C00000'); w2.getRange('M3:N3').setBackground('#7030A0');
  var A = 'ASO!$E$4:$E$' + last;
  var v2 = codes.map(function (c, i) {
    var k = 4 + i, r = seen[c], f = [];
    ['K', 'L', 'M', 'N', 'O', 'Q', 'R', 'S'].forEach(function (col) { f.push(F_('=SUMIFS(ASO!$' + col + '$4:$' + col + '$' + last + ',' + A + ',$B' + k + ')')); });
    return [r[0], c, r[2], r[3], F_('=COUNTIF(' + A + ',B' + k + ')'), F_('=COUNTIFS(' + A + ',B' + k + ',ASO!$Q$4:$Q$' + last + ',">0")')].concat(f)
      .concat([F_('=COUNTIFS(' + A + ',B' + k + ',ASO!$R$4:$R$' + last + ',"<>")'), F_('=COUNTIFS(' + A + ',B' + k + ',ASO!$U$4:$U$' + last + ',"Cần trình SD phê duyệt")')]);
  });
  w2.getRange(4, 1, codes.length, 16).setValues(v2);
  var t = 4 + codes.length, tot = ['TỔNG', '', '', ''];
  for (var c = 5; c <= 16; c++) { var L = String.fromCharCode(64 + c); tot.push('=SUM(' + L + '4:' + L + (t - 1) + ')'); }
  w2.getRange(t, 1, 1, 16).setValues([tot]).setFontWeight('bold').setBackground('#F2F2F2');
  w2.getRange(4, 5, codes.length + 1, 12).setNumberFormat('#,##0');
  w2.getRange(3, 1, codes.length + 2, 16).setBorder(true, true, true, true, true, true, '#BFBFBF', SpreadsheetApp.BorderStyle.SOLID);
  [20, 13, 20, 12, 10, 9, 10, 10, 10, 9, 9, 13, 11, 11, 11, 14].forEach(function (w, i) { w2.setColumnWidth(i + 1, w * 7.5); });
  w2.setRowHeight(3, 36); w2.setFrozenRows(3);

  var s1 = ss.getSheetByName('Sheet1') || ss.getSheetByName('Trang tính1');
  if (s1 && s1.getLastRow() === 0 && ss.getSheets().length > 2) ss.deleteSheet(s1);
  ss.setActiveSheet(ws);
  SpreadsheetApp.flush();
  ss.toast('Đã tạo xong ' + n + ' KH · ' + codes.length + ' tuyến', 'AQF 500', 10);
  Logger.log('Đã tạo xong ' + n + ' KH · ' + codes.length + ' tuyến · locale ' + loc + ' · dấu "' + SEP_ + '"');
}

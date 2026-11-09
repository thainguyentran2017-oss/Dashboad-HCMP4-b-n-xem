/**
 * Khoá file "Target ASO VIP Tết 2027 · Sales chốt · Bình Hồng"
 * NV chỉ được nhập ở 8 cột: CHỐT và Lý do giải trình của T11 LRB-AQF, T11 LRB CAN, T12 LRB-AQF, T12 LRB CAN
 * (cột K, L, O, P, S, T, W, X · từ dòng 5 trở xuống). Mọi ô khác chỉ chủ file sửa được.
 * Cách dùng: dán code → Lưu → chọn hàm khoaVIP → Chạy (cho phép quyền lần đầu).
 */
function khoaVIP() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sh = ss.getSheets()[0];
  // gỡ khoá cũ (nếu có) rồi khoá lại cả trang
  sh.getProtections(SpreadsheetApp.ProtectionType.SHEET).forEach(p => p.remove());
  sh.getProtections(SpreadsheetApp.ProtectionType.RANGE).forEach(p => p.remove());
  const p = sh.protect().setDescription('Chỉ số có sẵn đã khoá · NV chỉ nhập CHỐT và Lý do giải trình');
  const last = Math.max(sh.getLastRow(), 5);
  const mo = ['K', 'L', 'O', 'P', 'S', 'T', 'W', 'X'].map(c => sh.getRange(c + '5:' + c + last));
  p.setUnprotectedRanges(mo);
  // chỉ chủ file sửa được phần bị khoá
  const me = Session.getEffectiveUser();
  p.addEditor(me);
  p.removeEditors(p.getEditors().filter(u => u.getEmail() !== me.getEmail()));
  if (p.canDomainEdit()) p.setDomainEdit(false);
  Logger.log('Đã khoá xong: mở ' + mo.length + ' cột CHỐT/Lý do · dòng 5–' + last + ' · người sửa phần khoá: ' + p.getEditors().map(u => u.getEmail()).join(', '));
}

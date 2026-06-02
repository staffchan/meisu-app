const SPREADSHEET_ID = "13PtolESY7maJJenTjgbMM8-AEW-wFkyoL7vRb-4sLyc";
const SHEET_NAME = "シート1";

function doPost(e) {
  const spreadsheet = SpreadsheetApp.openById(SPREADSHEET_ID);
  const sheet = spreadsheet.getSheetByName(SHEET_NAME);
  if (!sheet) {
    throw new Error(`シート「${SHEET_NAME}」が見つかりません`);
  }

  const data = JSON.parse(e.postData.contents);
  const lock = LockService.getScriptLock();

  lock.waitLock(10000);
  try {
    ensureHeader(sheet);
    sheet.appendRow([
      data.name || "",
      data.birthdate || "",
      data.fullType || "",
      data.meisu1 || "",
      data.meisu2 || "",
      data.meisu3 || "",
      data.prevMeisu1 || "",
      data.prevMeisu2 || "",
      data.prevMeisu3 || "",
    ]);
  } finally {
    lock.releaseLock();
  }

  return ContentService
    .createTextOutput(JSON.stringify({ ok: true }))
    .setMimeType(ContentService.MimeType.JSON);
}

function doGet() {
  return ContentService
    .createTextOutput(JSON.stringify({ ok: true }))
    .setMimeType(ContentService.MimeType.JSON);
}

function ensureHeader(sheet) {
  if (sheet.getLastRow() > 0) {
    return;
  }

  sheet.appendRow([
    "名前",
    "生年月日",
    "タイプ",
    "第一の命数",
    "第二の命数",
    "第三の命数",
    "前日の第一の命数",
    "前日の第二の命数",
    "前日の第三の命数",
  ]);
}

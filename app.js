const APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxeDJiaRKPI3KC3UdT4sONSDDepSi1qcwh0EjIZ8m8ijYboY4YJAX8EdzNFKB7taFf1/exec";

const MEISU_FILES = [
  "data/命数_1950年代.csv",
  "data/命数_1960年代.csv",
  "data/命数_1970年代.csv",
  "data/命数_1980年代.csv",
  "data/命数_1990年代.csv",
  "data/命数_2000年代.csv",
  "data/命数_2010年代.csv",
  "data/命数_2020年代.csv",
];

const TEXT_FILE = "data/five_star_types_template.csv";

const TYPE_IMAGE_MAP = {
  "金の羅針盤座": "data/type_images/kin_rashinban.png",
  "銀の羅針盤座": "data/type_images/gin_rashinban.png",
  "金のインディアン座": "data/type_images/kin_indian.png",
  "銀のインディアン座": "data/type_images/gin_indian.png",
  "金の鳳凰座": "data/type_images/kin_houou.png",
  "銀の鳳凰座": "data/type_images/gin_houou.png",
  "金の時計座": "data/type_images/kin_tokei.png",
  "銀の時計座": "data/type_images/gin_tokei.png",
  "金のカメレオン座": "data/type_images/kin_kameleon.png",
  "銀のカメレオン座": "data/type_images/gin_kameleon.png",
  "金のイルカ座": "data/type_images/kin_iruka.png",
  "銀のイルカ座": "data/type_images/gin_iruka.png",
};

const state = {
  meisuRows: [],
  textRows: [],
  currentResult: null,
};

const elements = {
  birthScreen: document.querySelector("#birth-screen"),
  resultScreen: document.querySelector("#result-screen"),
  birthForm: document.querySelector("#birth-form"),
  saveForm: document.querySelector("#save-form"),
  year: document.querySelector("#birth-year"),
  month: document.querySelector("#birth-month"),
  day: document.querySelector("#birth-day"),
  loadMessage: document.querySelector("#load-message"),
  saveMessage: document.querySelector("#save-message"),
  backButton: document.querySelector("#back-button"),
  birthdateLabel: document.querySelector("#birthdate-label"),
  resultTitle: document.querySelector("#result-title"),
  mainMeisu: document.querySelector("#main-meisu"),
  meisu1: document.querySelector("#meisu-1"),
  meisu2: document.querySelector("#meisu-2"),
  meisu3: document.querySelector("#meisu-3"),
  typeImage: document.querySelector("#type-image"),
  fortuneHeading: document.querySelector("#fortune-heading"),
  fortuneTheme: document.querySelector("#fortune-theme"),
  basicText: document.querySelector("#basic-text"),
  loveText: document.querySelector("#love-text"),
  workText: document.querySelector("#work-text"),
  saveName: document.querySelector("#save-name"),
};

function fillSelect(select, values) {
  select.replaceChildren(
    ...values.map((value) => {
      const option = document.createElement("option");
      option.value = String(value);
      option.textContent = String(value);
      return option;
    })
  );
}

function updateDayOptions() {
  const year = Number(elements.year.value);
  const month = Number(elements.month.value);
  const lastDay = new Date(year, month, 0).getDate();
  const selectedDay = Number(elements.day.value) || 1;
  fillSelect(elements.day, Array.from({ length: lastDay }, (_, index) => index + 1));
  elements.day.value = String(Math.min(selectedDay, lastDay));
}

function parseCsv(text) {
  const rows = [];
  let row = [];
  let value = "";
  let inQuotes = false;
  const normalized = text.replace(/^\uFEFF/, "").replace(/\r\n/g, "\n").replace(/\r/g, "\n");

  for (let index = 0; index < normalized.length; index += 1) {
    const char = normalized[index];
    const next = normalized[index + 1];

    if (char === '"' && inQuotes && next === '"') {
      value += '"';
      index += 1;
    } else if (char === '"') {
      inQuotes = !inQuotes;
    } else if (char === "," && !inQuotes) {
      row.push(value);
      value = "";
    } else if (char === "\n" && !inQuotes) {
      row.push(value);
      if (row.some((cell) => cell.trim() !== "")) {
        rows.push(row);
      }
      row = [];
      value = "";
    } else {
      value += char;
    }
  }

  if (value || row.length) {
    row.push(value);
    rows.push(row);
  }

  const headers = rows.shift().map((header) => header.trim());
  return rows.map((cells) =>
    Object.fromEntries(headers.map((header, index) => [header, (cells[index] || "").trim()]))
  );
}

async function fetchCsv(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`${path} を読み込めませんでした`);
  }
  return parseCsv(await response.text());
}

async function loadData() {
  if (state.meisuRows.length && state.textRows.length) {
    return;
  }

  elements.loadMessage.textContent = "読み込み中...";
  const [meisuGroups, textRows] = await Promise.all([
    Promise.all(MEISU_FILES.map(fetchCsv)),
    fetchCsv(TEXT_FILE),
  ]);

  state.meisuRows = meisuGroups.flat();
  state.textRows = textRows;
  elements.loadMessage.textContent = "";
}

function getNumber(row, names) {
  for (const name of names) {
    if (row[name] !== undefined && row[name] !== "") {
      return Number(row[name]);
    }
  }
  return null;
}

function findMeisuRow(year, month, day) {
  return state.meisuRows.find(
    (row) => Number(row["年"]) === year && Number(row["月"]) === month && Number(row["日"]) === day
  );
}

function getStarType(meisu2) {
  if (meisu2 >= 1 && meisu2 <= 10) return "羅針盤座";
  if (meisu2 >= 11 && meisu2 <= 20) return "インディアン座";
  if (meisu2 >= 21 && meisu2 <= 30) return "鳳凰座";
  if (meisu2 >= 31 && meisu2 <= 40) return "時計座";
  if (meisu2 >= 41 && meisu2 <= 50) return "カメレオン座";
  if (meisu2 >= 51 && meisu2 <= 60) return "イルカ座";
  return "不明";
}

function formatDate(year, month, day) {
  return `${year}/${String(month).padStart(2, "0")}/${String(day).padStart(2, "0")}`;
}

function getPreviousResult(year, month, day) {
  const date = new Date(year, month - 1, day);
  date.setDate(date.getDate() - 1);
  const prevRow = findMeisuRow(date.getFullYear(), date.getMonth() + 1, date.getDate());

  if (!prevRow) {
    return { prevMeisu1: "", prevMeisu2: "", prevMeisu3: "" };
  }

  return {
    prevMeisu1: getNumber(prevRow, ["命数1", "第一の命数"]) ?? "",
    prevMeisu2: getNumber(prevRow, ["命数2", "第二の命数"]) ?? "",
    prevMeisu3: getNumber(prevRow, ["命数3", "第三の命数"]) ?? "",
  };
}

function createResult(year, month, day) {
  const row = findMeisuRow(year, month, day);

  if (!row) {
    throw new Error("該当するデータが見つかりませんでした");
  }

  const meisu1 = getNumber(row, ["命数1", "第一の命数"]);
  const meisu2 = getNumber(row, ["命数2", "第二の命数"]);
  const meisu3 = getNumber(row, ["命数3", "第三の命数"]);

  if ([meisu1, meisu2, meisu3].some((value) => value === null || Number.isNaN(value))) {
    throw new Error("命数データの列を読み取れませんでした");
  }

  const kinGin = year % 2 === 0 ? "金" : "銀";
  const starType = getStarType(meisu2);
  const fullType = `${kinGin}の${starType}`;
  const lastDigit = meisu2 % 10;
  const textRow = state.textRows.find(
    (text) => text.type === fullType && Number(text.meisu_last_digit) === lastDigit
  );

  return {
    year,
    month,
    day,
    birthdate: formatDate(year, month, day),
    fullType,
    lastDigit,
    meisu1,
    meisu2,
    meisu3,
    ...getPreviousResult(year, month, day),
    theme: textRow?.theme || "",
    basic: textRow?.basic || "（未入力）",
    love: textRow?.love || "（未入力）",
    work: textRow?.work || "（未入力）",
  };
}

function showResult(result) {
  state.currentResult = result;
  elements.birthScreen.hidden = true;
  elements.resultScreen.hidden = false;
  elements.birthScreen.classList.add("is-hidden");
  elements.resultScreen.classList.remove("is-hidden");
  elements.saveMessage.textContent = "";
  elements.saveMessage.classList.remove("is-error");
  elements.saveName.value = "";

  elements.birthdateLabel.textContent = `生年月日：${result.birthdate}`;
  elements.resultTitle.textContent = `✨ ${result.fullType}`;
  elements.mainMeisu.textContent = result.meisu2;
  elements.meisu1.textContent = result.meisu1;
  elements.meisu2.textContent = result.meisu2;
  elements.meisu3.textContent = result.meisu3;
  elements.fortuneHeading.textContent = `🌙 ${result.fullType} × 命数${result.lastDigit}`;
  elements.fortuneTheme.textContent = result.theme ? `🔮 ${result.theme}` : "";
  elements.basicText.textContent = result.basic;
  elements.loveText.textContent = result.love;
  elements.workText.textContent = result.work;

  const imagePath = TYPE_IMAGE_MAP[result.fullType];
  elements.typeImage.src = imagePath || "";
  elements.typeImage.alt = imagePath ? result.fullType : "";
  elements.typeImage.hidden = !imagePath;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function showBirthScreen() {
  state.currentResult = null;
  elements.birthScreen.hidden = false;
  elements.resultScreen.hidden = true;
  elements.resultScreen.classList.add("is-hidden");
  elements.birthScreen.classList.remove("is-hidden");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function setMessage(element, message, isError = false) {
  element.textContent = message;
  element.classList.toggle("is-error", isError);
}

async function saveResult(name) {
  if (!APPS_SCRIPT_URL) {
    throw new Error("保存先がまだ設定されていません");
  }

  const payload = {
    name,
    birthdate: state.currentResult.birthdate,
    fullType: state.currentResult.fullType,
    meisu1: state.currentResult.meisu1,
    meisu2: state.currentResult.meisu2,
    meisu3: state.currentResult.meisu3,
    prevMeisu1: state.currentResult.prevMeisu1,
    prevMeisu2: state.currentResult.prevMeisu2,
    prevMeisu3: state.currentResult.prevMeisu3,
  };

  await fetch(APPS_SCRIPT_URL, {
    method: "POST",
    mode: "no-cors",
    headers: {
      "Content-Type": "text/plain;charset=utf-8",
    },
    body: JSON.stringify(payload),
  });
}

function initialize() {
  fillSelect(elements.year, Array.from({ length: 74 }, (_, index) => 1950 + index));
  fillSelect(elements.month, Array.from({ length: 12 }, (_, index) => index + 1));
  updateDayOptions();

  elements.year.addEventListener("change", updateDayOptions);
  elements.month.addEventListener("change", updateDayOptions);
  elements.backButton.addEventListener("click", showBirthScreen);

  elements.birthForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    setMessage(elements.loadMessage, "");

    try {
      await loadData();
      showResult(
        createResult(
          Number(elements.year.value),
          Number(elements.month.value),
          Number(elements.day.value)
        )
      );
    } catch (error) {
      setMessage(elements.loadMessage, error.message, true);
    }
  });

  elements.saveForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = elements.saveForm.querySelector("button");
    const name = elements.saveName.value.trim();

    if (!name) {
      setMessage(elements.saveMessage, "名前を入力してください", true);
      return;
    }

    button.disabled = true;
    setMessage(elements.saveMessage, "スプレッドシートに送信中...");

    try {
      await saveResult(name);
      setMessage(elements.saveMessage, "Googleスプレッドシートに保存しました");
    } catch (error) {
      setMessage(elements.saveMessage, error.message, true);
    } finally {
      button.disabled = false;
    }
  });
}

initialize();

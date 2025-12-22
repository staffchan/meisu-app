import streamlit as st
import pandas as pd
import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import date, timedelta
from pathlib import Path

# =============================
# .env 読み込み
# =============================

# =============================
# Google Sheets 連携
# =============================
@st.cache_resource
def connect_to_gsheet():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    private_key = get_setting("GCP_PRIVATE_KEY", "").replace("\\n", "\n")
    client_email = get_setting("GCP_CLIENT_EMAIL")
    sheet_name = get_setting("SHEET_NAME", "命数記録シート")
    tab_name = get_setting("SHEET_TAB_NAME", "シート1")

    if not private_key or not client_email:
        st.error("❌ Google連携情報（Secrets）が見つかりません。")
        st.stop()

    service_account_info = {
        "type": "service_account",
        "private_key": private_key,
        "client_email": client_email,
        "token_uri": "https://oauth2.googleapis.com/token",
    }

    creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
    client = gspread.authorize(creds)

    try:
        return client.open(sheet_name).worksheet(tab_name)
    except Exception as e:
        st.error(f"❌ シート接続エラー: {e}")
        st.stop()

    service_account_info = {
        "type": "service_account",
        "private_key": private_key,
        "client_email": client_email,
        "token_uri": "https://oauth2.googleapis.com/token",
    }

    creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
    client = gspread.authorize(creds)

    try:
        return client.open(sheet_name).worksheet(tab_name)
    except Exception as e:
        st.error(f"❌ シート接続エラー: {e}")
        st.stop()
def get_setting(key: str, default: str = ""):
    return st.secrets.get(key, os.getenv(key, default))
sheet = connect_to_gsheet()

# =============================
# 命数2 → 座の分類
# =============================
def get_star_type(meisu2: int) -> str:
    if 1 <= meisu2 <= 10:
        return "羅針盤座"
    elif 11 <= meisu2 <= 20:
        return "インディアン座"
    elif 21 <= meisu2 <= 30:
        return "鳳凰座"
    elif 31 <= meisu2 <= 40:
        return "時計座"
    elif 41 <= meisu2 <= 50:
        return "カメレオン座"
    elif 51 <= meisu2 <= 60:
        return "イルカ座"
    return "不明"

# =============================
# CSV 読み込み（命数表）
# =============================
@st.cache_data
def load_all_data() -> pd.DataFrame:
    data_dir = "data"
    dfs = []
    for file in sorted(os.listdir(data_dir)):
        if file.endswith(".csv") and "命数" in file:
            dfs.append(pd.read_csv(os.path.join(data_dir, file)))
    if not dfs:
        return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True)

# =============================
# CSV 読み込み（タイプ文章）
# =============================
@st.cache_data
def load_five_star_texts() -> pd.DataFrame:
    path = "data/five_star_types_template.csv"
    if os.path.exists(path):
        df = pd.read_csv(path, encoding="utf-8-sig")
    else:
        df = pd.DataFrame(columns=["type", "meisu_last_digit", "theme", "basic", "love", "work"])

    df.columns = df.columns.str.strip()
    df["type"] = df["type"].astype(str).str.strip()
    df["meisu_last_digit"] = df["meisu_last_digit"].astype(int)
    return df

df = load_all_data()
texts_df = load_five_star_texts()

# =============================
# ページ設定
# =============================
st.set_page_config(page_title="結果", layout="wide")

# =============================
# CSS（Hannari共通 + サイドバー非表示 + レイアウト）
# =============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Hannari&display=swap');

:root, html, body,
[data-testid="stAppViewContainer"], [data-testid="stApp"],
section, main, div, p, span, label,
h1, h2, h3, h4, h5, h6, button, input, textarea, select {
  font-family: "Hannari","Hiragino Mincho ProN","Yu Mincho",serif !important;
}

/* サイドバーを消す */
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stAppViewContainer"] { padding-left: 0 !important; }

/* コンテンツ幅 */
.block-container{
  max-width: 860px;
  padding-top: 3.2rem;
  padding-bottom: 4rem;
}

/* タイプ表示を主役に */
.type-title{
  font-size: clamp(26px, 3.0vw, 42px);
  letter-spacing: 0.06em;
  margin: 0 0 0.6rem 0;
}

/* 命数カード */
.meisu-card{
  background: rgba(255,255,255,0.72);
  border: 1px solid rgba(255,255,255,0.45);
  border-radius: 18px;
  padding: 18px 18px 12px 18px;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.10);
  margin: 1.0rem 0 1.0rem 0;
}

.meisu-main{
  font-size: clamp(22px, 2.2vw, 30px);
  margin: 0 0 0.5rem 0;
}

.meisu-row{
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  margin: 0.3rem 0 0 0;
}

.meisu-pill{
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(245,246,248,0.96);
  border: 1px solid rgba(0,0,0,0.06);
}

/* 画像（中央・小さめ） */
.type-image-wrap{
  text-align: center;
  margin: 0.6rem 0 1.6rem 0;
  opacity: 0.98;
}
.type-image-wrap img{
  max-width: 360px;
}

/* ボタン */
.stButton > button{
  border-radius: 999px !important;
  padding: 8px 18px !important;
  font-weight: 700 !important;
}

/* === スマホ上部に出る sidebar トグル（文字で keyboard_double_arrow_right になるやつ）を徹底的に消す === */

/* 既存 testid（あなたの環境） */
[data-testid="stSidebarCollapsedControl"] {
  display: none !important;
}
[data-testid="stSidebarCollapsedControl"] * {
  display: none !important;
}

/* Streamlitの版差対策（別名になることがある） */
div[class*="sidebarCollapsedControl"],
div[class*="collapsedControl"] {
  display: none !important;
}

/* ボタンがaria-labelで出る版 */
button[aria-label="Show sidebar"],
button[aria-label="Hide sidebar"],
button[title="Open sidebar"],
button[title="Close sidebar"] {
  display: none !important;
}

/* それでも残るときの最終手段：ヘッダー左側のコントロールを消す */
[data-testid="stHeader"] button {
  display: none !important;
}
/* === ダークモードのときだけ、明るいカード内の文字を黒寄りに固定 === */
@media (prefers-color-scheme: dark) {{
  .meisu-card,
  .meisu-card * ,
  .meisu-pill,
  .meisu-pill *  {{
    color: rgba(0,0,0,0.82) !important;
  }}

  /* もし他にも“白背景の箱”があるならここに足す */
  .birth-form,
  .birth-form *  {{
    color: rgba(0,0,0,0.82) !important;
  }}
}}

</style>
""", unsafe_allow_html=True)

# =============================
# session_state（birth.py から受け取り）
# =============================
if not all(k in st.session_state for k in ["birth_year", "birth_month", "birth_day"]):
    st.warning("生年月日が未入力です。入力画面へ戻ってください。")
    if st.button("◀ 生年月日入力へ戻る"):
        st.switch_page("birth.py")
    st.stop()

year = int(st.session_state["birth_year"])
month = int(st.session_state["birth_month"])
day = int(st.session_state["birth_day"])
birthdate_str = f"{year}/{month:02}/{day:02}"

if df.empty:
    st.error("命数データCSVが読み込めませんでした。（dataフォルダ内の命数CSVを確認してね）")
    st.stop()

# 今日の命数
result = df[(df["年"] == year) & (df["月"] == month) & (df["日"] == day)]
if result.empty:
    st.warning("該当するデータが見つかりませんでした。")
    if st.button("◀ 生年月日入力へ戻る"):
        st.switch_page("birth.py")
    st.stop()

row = result.iloc[0]
meisu1 = int(float(row["命数1"]))
meisu2 = int(float(row["命数2"]))
meisu3 = int(float(row["命数3"]))

# タイプ
kin_gin = "金" if year % 2 == 0 else "銀"
star_type = get_star_type(meisu2)
full_type = f"{kin_gin}の{star_type}"
last_digit = int(str(meisu2)[-1])

# 画像マップ
TYPE_IMAGE_MAP = {
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
}

# ✅ 前日の命数（“単純に -1” じゃなく、前日の日付でCSVを引く）
try:
    d = date(year, month, day)
    prev = d - timedelta(days=1)

    prev_row = df[(df["年"] == prev.year) & (df["月"] == prev.month) & (df["日"] == prev.day)]
    if not prev_row.empty:
        prev_meisu1 = int(float(prev_row.iloc[0]["命数1"]))
        prev_meisu2 = int(float(prev_row.iloc[0]["命数2"]))
        prev_meisu3 = int(float(prev_row.iloc[0]["命数3"]))
    else:
        prev_meisu1, prev_meisu2, prev_meisu3 = "", "", ""
except Exception:
    prev_meisu1, prev_meisu2, prev_meisu3 = "", "", ""

# =============================
# 表示（タイプ → 命数 → 画像 → 文章）
# =============================
st.markdown(f'<div class="type-title">✨ {full_type}</div>', unsafe_allow_html=True)
st.caption(f"生年月日：{birthdate_str}")

st.markdown(
    f"""
<div class="meisu-card">
  <div class="meisu-main">命数 <b>{meisu2}</b></div>
  <div class="meisu-row">
    <div class="meisu-pill">第一の命数：<b>{meisu1}</b></div>
    <div class="meisu-pill">第二の命数：<b>{meisu2}</b></div>
    <div class="meisu-pill">第三の命数：<b>{meisu3}</b></div>
  </div>
</div>
""",
    unsafe_allow_html=True
)

# ✅ 画像はここだけ（1回だけ表示）
img_path = TYPE_IMAGE_MAP.get(full_type)
if img_path and Path(img_path).exists():
    st.markdown('<div class="type-image-wrap">', unsafe_allow_html=True)
    st.image(img_path, width=360)
    st.markdown("</div>", unsafe_allow_html=True)

# =============================
# 文章（basic/love/work）
# =============================
text_row = texts_df[(texts_df["type"] == full_type.strip()) & (texts_df["meisu_last_digit"] == last_digit)]

st.markdown(f"## 🌙 {full_type} × 命数{last_digit}")

if text_row.empty:
    st.info("このタイプと命数に対応する文章がまだ登録されていません。")
else:
    theme = text_row.iloc[0].get("theme", "")
    basic_text = text_row.iloc[0].get("basic", "")
    love_text = text_row.iloc[0].get("love", "")
    work_text = text_row.iloc[0].get("work", "")

    if theme:
        st.markdown(f"#### 🔮 {theme}")

    st.markdown("### 💫 基本性格")
    st.write(basic_text if basic_text else "（未入力）")

    st.markdown("### 💞 恋愛運")
    st.write(love_text if love_text else "（未入力）")

    st.markdown("### 💼 仕事運")
    st.write(work_text if work_text else "（未入力）")

# =============================
# 保存ボタン（最下部）
# =============================
st.divider()
st.subheader("📥 結果を保存する")

with st.form("save_form"):
    name = st.text_input("保存する名前（任意）を入力")
    submitted = st.form_submit_button("保存する")

if submitted:
    if not name:
        st.warning("⚠️ 名前を入力してください")
        st.stop()

    st.write("📤 スプレッドシートに送信中...")

    try:
        sheet.append_row([
            name,
            birthdate_str,
            full_type,
            meisu1,
            meisu2,
            meisu3,
            prev_meisu1,  # ✅ 前日の命数1（CSVから）
            prev_meisu2,  # ✅ 前日の命数2（CSVから）
            prev_meisu3,  # ✅ 前日の命数3（CSVから）
        ])
        st.success("✅ Googleスプレッドシートに保存しました！")
    except Exception as e:
        st.error("❌ 保存エラー発生！")
        st.exception(e)

st.divider()

# もう一度占う
if st.button("🔁 もう一度占う"):
    for k in ["birth_year", "birth_month", "birth_day"]:
        st.session_state.pop(k, None)
    st.switch_page("birth.py")
import base64
from pathlib import Path
import streamlit as st

# -----------------------------
# Page Config（最上部）
# -----------------------------
st.set_page_config(page_title="生年月日入力", layout="wide")

# -----------------------------
# Base64 画像
# -----------------------------
def get_base64_image(path: str) -> str:
    p = Path(path)
    if not p.exists():
        st.error(f"背景画像が見つかりません: {p.resolve()}")
        st.stop()
    return base64.b64encode(p.read_bytes()).decode("utf-8")

bg_b64 = get_base64_image("data/birth_background.png")

# -----------------------------
# CSS（Hannari固定 / 背景切れ対策 / サイドバー非表示）
# -----------------------------
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Hannari&display=swap');

/* ===== フォント（全体に強制） ===== */
:root, html, body,
[data-testid="stAppViewContainer"], [data-testid="stApp"],
[data-testid="stHeader"], [data-testid="stSidebar"],
section, main, div, p, span, label,
h1, h2, h3, h4, h5, h6, button, input, textarea, select {{
  font-family: "Hannari","Hiragino Mincho ProN","Yu Mincho",serif !important;
}}

/* ===== サイドバーを消す（ナビも消える） ===== */
[data-testid="stSidebar"] {{
  display: none !important;
}}
/* サイドバー消すと左詰めになるケースの保険 */
[data-testid="stAppViewContainer"] {{
  padding-left: 0 !important;
}}

/* ===== 背景画像（上が切れにくい） ===== */
[data-testid="stAppViewContainer"], [data-testid="stApp"] {{
  background-image: url("data:image/png;base64,{bg_b64}");
  background-repeat: no-repeat;
  background-size: contain;           /* 切らない */
  background-position: center 80px;   /* 少し下げる */
  background-attachment: scroll;
  min-height: 120vh;                  /* “見える領域”を増やす */
}}

/* ===== レイアウト（中央寄せ） ===== */
.block-container {{
  max-width: 860px;
  padding-top: 9rem;      /* ここで全体を下げる（背景の上切れ対策も兼ねる） */
  padding-bottom: 8rem;
}}

/* ===== タイトル（1行固定 + 自動縮小） ===== */
h1 {{
  white-space: nowrap !important;
  font-size: clamp(26px, 3.0vw, 40px) !important;
  line-height: 1.25 !important;
  letter-spacing: 0.06em;
  margin-bottom: 1.6rem;
}}

/* ===== ラベル太字 ===== */
.birth-form label {{
  font-weight: 700 !important;
  letter-spacing: 0.04em;
}}

/* ===== 入力幅（小さめ） ===== */
.birth-form div[data-baseweb="select"] {{
  max-width: 420px;
}}

/* selectbox見た目 */
.birth-form div[data-baseweb="select"] > div {{
  border-radius: 14px !important;
  background-color: rgba(245,246,248,0.96);
}}

/* ボタン */
.stButton > button {{
  border-radius: 999px !important;
  padding: 8px 18px !important;
  font-weight: 700 !important;
  margin-top: 1.2rem;
}}

/* === スマホ上部に出る sidebar トグル（文字で keyboard_double_arrow_right になるやつ）を徹底的に消す === */

/* 既存 testid（あなたの環境） */
[data-testid="stSidebarCollapsedControl"] {{
  display: none !important;
}}
[data-testid="stSidebarCollapsedControl"] * {{
  display: none !important;
}}

/* Streamlitの版差対策（別名になることがある） */
div[class*="sidebarCollapsedControl"],
div[class*="collapsedControl"] {{
  display: none !important;
}}

/* ボタンがaria-labelで出る版 */
button[aria-label="Show sidebar"],
button[aria-label="Hide sidebar"],
button[title="Open sidebar"],
button[title="Close sidebar"] {{
  display: none !important;
}}

/* それでも残るときの最終手段：ヘッダー左側のコントロールを消す */
[data-testid="stHeader"] button {{
  display: none !important;
}}

/* ===== スマホ用だけ背景を調整 ===== */
@media (max-width: 768px) {{

  [data-testid="stAppViewContainer"],
  [data-testid="stApp"] {{
    background-size: 130% !important;
    background-position: center top !important;
    min-height: 100vh !important;
  }}

  .block-container {{
    padding-top: 6rem !important;
  }}
}}
</style>
""",
    unsafe_allow_html=True,
)
# -----------------------------
# UI
# -----------------------------
st.markdown('<div class="birth-form">', unsafe_allow_html=True)

st.title("生年月日を入力してください")

year = st.selectbox("西暦（年）", list(range(1950, 2024)), index=0)
month = st.selectbox("月", list(range(1, 13)), index=0)
day = st.selectbox("日", list(range(1, 32)), index=0)

if st.button("▶ 次へ"):
    st.session_state["birth_year"] = year
    st.session_state["birth_month"] = month
    st.session_state["birth_day"] = day
    st.switch_page("pages/result.py")

st.markdown("</div>", unsafe_allow_html=True)
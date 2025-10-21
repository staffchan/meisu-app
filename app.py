import streamlit as st
import pandas as pd
import os
import gspread
from google.oauth2.service_account import Credentials

# ===== Google Sheets連携（Streamlit Cloud用） =====
@st.cache_resource
def connect_to_gsheet():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scope
    )
    client = gspread.authorize(creds)
    sheet = client.open("命数記録シート").sheet1  # スプレッドシート名と一致させてね
    return sheet

sheet = connect_to_gsheet()

# ===== 欲の傾向マッピング =====
yoku_dict = {
    (1, 2): "自我欲（自分中心に考えたい欲）",
    (3, 4): "食欲・性欲（楽しみたい欲）",
    (5, 6): "金欲・財欲（得をしたい欲）",
    (7, 8): "権力・支配欲（上に立ちたい欲）",
    (9, 0): "創作欲（才能を発揮したい欲）"
}

# 命数の意味
meisu_meanings = {
    43: "自由と変化を求めるクリエイター気質",
    44: "着実に努力することで道が開けるタイプ",
    48: "周囲に調和をもたらす平和主義者",
    # 必要に応じて追加
}

# 命数→座の分類
def get_star_type(meisu2):
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
    else:
        return "不明"

# ===== データ読み込み（命数データCSV） =====
@st.cache_data
def load_all_data():
    data_dir = "data"
    dfs = []
    for file in sorted(os.listdir(data_dir)):
        if file.endswith(".csv"):
            df = pd.read_csv(os.path.join(data_dir, file))
            dfs.append(df)
    all_data = pd.concat(dfs, ignore_index=True)
    return all_data

df = load_all_data()

# ===== UI =====
st.title("五星三心占い")
years = sorted(df['年'].unique())
selected_year = st.selectbox("西暦（年）", years)
selected_month = st.selectbox("月", list(range(1, 13)))
selected_day = st.selectbox("日", list(range(1, 32)))

if st.button("検索"):
    result = df[
        (df['年'] == selected_year) &
        (df['月'] == selected_month) &
        (df['日'] == selected_day)
    ]

    if not result.empty:
        row = result.iloc[0]
        meisu1 = int(float(row['命数1']))
        meisu2 = int(float(row['命数2']))
        meisu3 = int(float(row['命数3']))

        kin_gin = "金" if selected_year % 2 == 0 else "銀"
        star_type = get_star_type(meisu2)
        full_type = f"{kin_gin}の{star_type}"

        last_digit = int(str(meisu2)[-1])
        yoku = next((v for k, v in yoku_dict.items() if last_digit in k), "不明")

        meaning = meisu_meanings.get(meisu2, "意味データ未登録")

        st.subheader(f"🌟 あなたの五星三心タイプ：**{full_type}**")
        st.markdown(f"🔹 第一の命数（過去）: {meisu1}")
        st.markdown(f"🔸 第二の命数（現在）: {meisu2}")
        st.markdown(f"🔹 第三の命数（未来）: {meisu3}")
        st.markdown(f"📖 意味：{meaning}")
        st.markdown(f"🔥 欲の傾向：{yoku}")

        # ===== 保存欄 =====
        name = st.text_input("保存する名前（任意）を入力")
        if st.button("保存する"):
            if not name:
                st.warning("名前を入力してください。")
            else:
                birthdate = f"{selected_year}/{selected_month:02}/{selected_day:02}"
                prev1 = meisu1 - 1 if meisu1 > 1 else ""
                prev2 = meisu2 - 1 if meisu2 > 1 else ""
                prev3 = meisu3 - 1 if meisu3 > 1 else ""

                try:
                    sheet.append_row([
                        name,
                        birthdate,
                        full_type,
                        meisu1,
                        meisu2,
                        meisu3,
                        prev1,
                        prev2,
                        prev3
                    ])
                    st.success("✅ Googleスプレッドシートに保存しました！")
                except Exception as e:
                    st.error(f"❌ 保存中にエラーが発生しました: {e}")
    else:
        st.warning("該当するデータが見つかりませんでした。")

import streamlit as st
import pandas as pd
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta

# ===== Google Sheets連携 =====
@st.cache_resource
def connect_to_gsheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json", scope
    )
    client = gspread.authorize(creds)
    sheet = client.open("命数記録シート").sheet1  # ←スプレッドシート名に合わせてね
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

# 命数の意味（仮）
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

# ===== データ読み込み =====
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

# ===== UI：タイトルとセレクト =====
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

        # 結果をセッションに保存
        st.session_state["result_data"] = {
            "meisu1": meisu1,
            "meisu2": meisu2,
            "meisu3": meisu3,
            "full_type": full_type,
            "birthdate": f"{selected_year}/{selected_month:02}/{selected_day:02}"
        }

        st.subheader(f"🌟 あなたの五星三心タイプ：**{full_type}**")
        st.markdown(f"🔹 第一の命数（過去）: {meisu1}")
        st.markdown(f"🔸 第二の命数（現在）: {meisu2}")
        st.markdown(f"🔹 第三の命数（未来）: {meisu3}")
        st.markdown(f"📖 意味：{meaning}")
        st.markdown(f"🔥 欲の傾向：{yoku}")
    else:
        st.warning("該当するデータが見つかりませんでした。")

# ===== 保存欄（検索の外） =====
if "result_data" in st.session_state:
    st.markdown("---")
    st.subheader("🔖 結果を保存")

    name = st.text_input("保存する名前（任意）を入力", key="name_input")

    if st.button("保存する", key="save_button"):
        data = st.session_state["result_data"]
        birthdate_str = data["birthdate"]
        birth_dt = datetime.strptime(birthdate_str, "%Y/%m/%d")
        prev_dt = birth_dt - timedelta(days=1)

        # 前日の命数を取得
        prev_row = df[
            (df['年'] == prev_dt.year) &
            (df['月'] == prev_dt.month) &
            (df['日'] == prev_dt.day)
        ]

        if not prev_row.empty:
            prev_row = prev_row.iloc[0]
            prev1 = int(float(prev_row['命数1']))
            prev2 = int(float(prev_row['命数2']))
            prev3 = int(float(prev_row['命数3']))
        else:
            prev1 = prev2 = prev3 = ""

        try:
            sheet.append_row([
                name,
                birthdate_str,
                data["full_type"],
                data["meisu1"],
                data["meisu2"],
                data["meisu3"],
                prev1,
                prev2,
                prev3
            ])
            st.success("✅ Googleスプレッドシートに保存しました！")
        except Exception as e:
            st.error(f"❌ 保存中にエラーが発生しました: {e}")
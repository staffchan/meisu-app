import pandas as pd

# ===== 五星三心 12タイプ =====
types = [
    "金の羅針盤座", "銀の羅針盤座",
    "金のインディアン座", "銀のインディアン座",
    "金の鳳凰座", "銀の鳳凰座",
    "金の時計座", "銀の時計座",
    "金のカメレオン座", "銀のカメレオン座",
    "金のイルカ座", "銀のイルカ座"
]

# ===== CSVの内容を構築 =====
rows = []
for t in types:
    for n in range(10):
        rows.append({
            "type": t,
            "meisu_last_digit": n,
            "basic": "",  # 基本性格
            "love": "",   # 恋愛傾向
            "work": ""    # 仕事運
        })

# ===== DataFrameに変換して保存 =====
df = pd.DataFrame(rows)
output_path = "data/five_star_types_template.csv"
df.to_csv(output_path, index=False, encoding="utf-8-sig")

print("✅ five_star_types_template.csv を作成しました！")
print(f"保存場所: {output_path}")
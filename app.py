
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="競馬予想アプリ舜")
st.title("競馬予想アプリ舜　【復旧完了】")

# データ読み込み
file = Path("data_full.csv")
if file.exists():
    df = pd.read_csv(file)
    st.success(f"データ読み込み完了！ 現在 {len(df)}頭 / {df["レース名"].nunique() if "レース名" in df.columns else 0}レース")
else:
    df = pd.DataFrame()
    st.info("まだデータがないで！下から登録してな")

# 手動登録（今まで通り爆速で入れるやつ）
with st.form("input"):
    st.write("レース情報")
    col1,col2 = st.columns(2)
    race_date = col1.date_input("日付")
    race_name = col2.text_input("レース名","有馬記念など")

    st.write("全頭入力（着順は1〜3位だけ入れればOK）")
    edited = st.data_editor(
        pd.DataFrame(columns=["馬名","人気","オッズ","斤量","馬体重","馬番","馬体重","着順"]),
        num_rows="dynamic"
    )

    if st.form_submit_button("登録！！"):
        if len(edited) > 0 and edited["馬名"].str.strip().ne("").any():
            edited["着順"] = pd.to_numeric(edited["着順"], errors="coerce").fillna(99)
            edited["日付"] = str(race_date)
            edited["レース名"] = race_name
            new_df = pd.concat([df, edited], ignore_index=True)
            new_df.to_csv("data_full.csv", index=False)
            st.success(f"登録完了！ → {len(new_df)}頭になったで！")
            st.balloons()
            st.rerun()
        else:
            st.error("馬名入れてな～")

st.write("今までのデータは全部残ってるから安心して！また明日ガチ版作るわ！")

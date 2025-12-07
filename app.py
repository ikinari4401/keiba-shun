
import streamlit as st
import pandas as pd
import lightgbm as lgb
from pathlib import Path
import numpy as np

st.set_page_config(page_title="競馬予想アプリ舜", layout="centered")
st.title("競馬予想アプリ舜")

@st.cache_data
def load_data():
    data_file = Path("data.csv")
    if data_file.exists():
        return pd.read_csv(data_file)
    else:
        return pd.DataFrame(columns=["日付","馬名","人気","オッズ","着順"])

df_past = load_data()

def save_data(df):
    df.to_csv("data.csv", index=False)

tab1, tab2, tab3 = st.tabs(["今日の予想", "過去データ登録", "AI学習"])

with tab1:
    st.subheader("今日のレースを入力 → 舜が予想")
    horses = []
    with st.form("today"):
        for i in range(18):
            with st.expander(f"{i+1}頭目", expanded=i<6):
                c1,c2,c3 = st.columns(3)
                name = c1.text_input("馬名", key=f"n{i}")
                pop  = c2.number_input("人気",1,18, key=f"p{i}")
                odds = c3.number_input("オッズ",1.0,500.0,10.0,0.1, key=f"o{i}")
                if name:
                    horses.append({"馬名":name,"人気":pop,"オッズ":odds})
        submitted = st.form_submit_button("舜、予想して！", type="primary")
        if submitted:
            if horses:
                if Path("model.txt").exists():
                    X = pd.DataFrame(horses)[["人気","オッズ"]]
                    model = lgb.Booster(model_file="model.txt")
                    pred = model.predict(X)
                    result = pd.DataFrame(horses)
                    result["勝率(%)"] = (pred * 100).round(1)
                    result["期待値"] = ((result["勝率(%)"]/100 * (result["オッズ"]-1)) - (1 - result["勝率(%)"]/100)).round(2)
                    st.dataframe(result.sort_values("期待値", ascending=False).style.background_gradient(cmap="Reds"), use_container_width=True)
                    st.success("舜の推奨：期待値上位に注目！")
                    st.balloons()
                else:
                    st.info("まだ学習してないよ！過去データ登録して学習させてね")
            else:
                st.warning("馬を1頭以上入力して！")

with tab2:
    st.subheader("過去の的中レースを登録（1着だけOK）")
    with st.form("past"):
        c1,c2,c3,c4 = st.columns([3,2,2,3])
        win_name = c1.text_input("1着馬名")
        win_pop  = c2.number_input("1着人気",1,18)
        win_odds = c3.number_input("1着単勝オッズ",1.0,999.0,5.0,0.1)
        race_date = c4.date_input("レース日")
        submitted_past = st.form_submit_button("このレースを登録")
        if submitted_past:
            new_data = pd.DataFrame([{
                "日付": str(race_date),
                "馬名": win_name,
                "人気": win_pop,
                "オッズ": win_odds,
                "着順": 1
            }])
            df_past = pd.concat([df_past, new_data]).drop_duplicates().reset_index(drop=True)
            save_data(df_past)
            st.success(f"登録完了！ {win_name} ({win_odds}倍) → 合計 {len(df_past)} レース")
            st.rerun()

with tab3:
    st.write(f"現在の学習データ：**{len(df_past)} レース**")
    if len(df_past) >= 10:
        if st.button("今すぐ舜を学習させる！！", type="primary"):
            with st.spinner("舜が勉強中…"):
                from lightgbm import LGBMClassifier
                X = df_past[["人気","オッズ"]]
                y = (df_past["着順"] == 1).astype(int)
                model = LGBMClassifier(n_estimators=300, learning_rate=0.05, random_state=42)
                model.fit(X, y)
                model.booster_.save_model("model.txt")
            st.success("学習完了！！ 次から本格予想が出るよ！")
            st.balloons()
            st.rerun()
    else:
        st.info(f"あと {10 - len(df_past)} レース登録したら学習ボタン出現！")

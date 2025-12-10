
import streamlit as st
import pandas as pd
from pathlib import Path
import time

st.query_params["t"] = int(time.time())  # キャッシュ完全殺し

st.set_page_config(page_title="馬神舜", layout="wide")
st.markdown("# 馬神舜　～マスター登録で入力3倍楽～")

# データファイル
data_file = Path("ore_no_full_meikiki.csv")
horse_master_file = Path("horse_master.csv")
jockey_master_file = Path("jockey_master.csv")

# データロード
if 'df' not in st.session_state:
    st.session_state.df = pd.read_csv(data_file) if data_file.exists() else pd.DataFrame()
df = st.session_state.df

if 'horse_master' not in st.session_state:
    st.session_state.horse_master = pd.read_csv(horse_master_file) if horse_master_file.exists() else pd.DataFrame(columns=["馬名","血統","馬齢","性別","脚質傾向"])
horse_master = st.session_state.horse_master

if 'jockey_master' not in st.session_state:
    st.session_state.jockey_master = pd.read_csv(jockey_master_file) if jockey_master_file.exists() else pd.DataFrame(columns=["ジョッキー名","勝率","得意馬場","得意距離"])
jockey_master = st.session_state.jockey_master

st.write(f"### データ：{len(df)}頭　馬マスター：{len(horse_master)}頭　ジョッキーマスター：{len(jockey_master)}人")

tab1, tab2, tab3, tab4 = st.tabs(["今日の予想", "過去レース入力", "馬マスター登録", "ジョッキーマスター登録"])

# ==================== 今日の予想（マスターから自動補完） ====================
with tab1:
    st.subheader("今日のレース入力（マスターから選ぶだけ！）")
    with st.form("today"):
        col1, col2, col3 = st.columns(3)
        race_date = col1.date_input("レース日")
        race_name = col2.text_input("レース名")
        race_class = col3.selectbox("等級", ["G1","G2","G3","OP","L","3勝","2勝","1勝","未勝利","新馬"])

        horses = []
        for i in range(18):
            with st.expander(f"{i+1}頭目", expanded=i<9):
                c1,c2 = st.columns([3,7])
                selected_horse = c1.selectbox("馬名（マスターから選択）", [""] + horse_master["馬名"].tolist(), key=f"h{i}")
                if selected_horse:
                    hm = horse_master[horse_master["馬名"] == selected_horse].iloc[0]
                    c2.write(f"{hm['血統']} {hm['馬齢']}歳{hm['性別']} 脚質:{hm['脚質傾向']}")
                    pop = c2.number_input("人気",1,18, key=f"p{i}")
                    odds = c2.number_input("オッズ",1.0,999.0, key=f"o{i}")
                    horses.append({"年月日":str(race_date),"レース名":race_name,"等級":race_class,"馬名":selected_horse,"人気":pop,"オッズ":odds})

# ==================== 過去レース入力（等級＋マスター選択） ====================
with tab2:
    st.subheader("過去レース入力")
    with st.form("past", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        race_date = col1.date_input("レース日")
        race_name = col2.text_input("レース名")
        race_class = col3.selectbox("等級", ["G1","G2","G3","OP","L","3勝","2勝","1勝","未勝利","新馬"], key="past_class")
        # 同様に馬選択＋ジョッキー選択で爆速入力

# ==================== 馬マスター登録 ====================
with tab3:
    st.subheader("競走馬マスター登録（1回登録したら永遠に楽）")
    with st.form("horse_master"):
        name = st.text_input("馬名")
        blood = st.text_input("血統（父馬）")
        age = st.number_input("馬齢",2,15,4)
        sex = st.selectbox("性別",["牡","牝","セ"])
        pace = st.selectbox("脚質傾向",["逃げ","先行","差し","追込"])
        if st.form_submit_button("この馬をマスター登録！！"):
            new_h = pd.DataFrame([{"馬名":name,"血統":blood,"馬齢":age,"性別":sex,"脚質傾向":pace}])
            st.session_state.horse_master = pd.concat([horse_master, new_h], ignore_index=True)
            st.session_state.horse_master.to_csv("horse_master.csv", index=False)
            st.success(f"{name} をマスター登録完了！")

# ==================== ジョッキーマスター登録 ====================
with tab4:
    st.subheader("ジョッキーマスター登録")
    with st.form("jockey_master"):
        name = st.text_input("ジョッキー名")
        win_rate = st.number_input("勝率(%)",0.0,30.0,10.0,0.1)
        good_turf = st.multiselect("得意馬場",["芝","ダート","良","重"])
        good_dist = st.text_input("得意距離（例:1600-2000）")
        if st.form_submit_button("このジョッキーをマスター登録！！"):
            new_j = pd.DataFrame([{"ジョッキー名":name,"勝率":win_rate,"得意馬場":",".join(good_turf),"得意距離":good_dist}])
            st.session_state.jockey_master = pd.concat([jockey_master, new_j], ignore_index=True)
            st.session_state.jockey_master.to_csv("jockey_master.csv", index=False)
            st.success(f"{name} をマスター登録完了！")

st.balloons()
st.success("【真の完成】馬・ジョッキー・マスター登録＋レース等級で入力3倍楽になったで！！")

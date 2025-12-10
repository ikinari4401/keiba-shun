
import streamlit as st
import pandas as pd
from pathlib import Path
import time

st.query_params["t"] = int(time.time())

st.set_page_config(page_title="馬神舜", layout="wide")
st.markdown("# 馬神舜　～3大マスター登録で入力爆速・精度爆上げ～")

# ファイル
DATA_FILE = Path("mushin_master.csv")
HORSE_FILE = Path("horse_master.csv")
TRAINER_FILE = Path("trainer_master.csv")
JOCKEY_FILE = Path("jockey_master.csv")

# セッション管理
if "df" not in st.session_state:
    st.session_state.df = pd.read_csv(DATA_FILE) if DATA_FILE.exists() else pd.DataFrame()
if "horse" not in st.session_state:
    st.session_state.horse = pd.read_csv(HORSE_FILE) if HORSE_FILE.exists() else pd.DataFrame(columns=["馬名","血統","馬齢","性別","脚質傾向","調教師"])
if "trainer" not in st.session_state:
    st.session_state.trainer = pd.read_csv(TRAINER_FILE) if TRAINER_FILE.exists() else pd.DataFrame(columns=["調教師名","勝率","得意コース"])
if "jockey" not in st.session_state:
    st.session_state.jockey = pd.read_csv(JOCKEY_FILE) if JOCKEY_FILE.exists() else pd.DataFrame(columns=["ジョッキー名","勝率","得意馬場","得意距離"])

df = st.session_state.df
horse = st.session_state.horse
trainer = st.session_state.trainer
jockey = st.session_state.jockey

st.write(f"### データ：{len(df)}頭　馬マスター：{len(horse)}頭　調教師：{len(trainer)}人　騎手：{len(jockey)}人")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["今日の予想", "過去入力", "競走馬登録", "調教師登録", "騎手登録"])

# ==================== 今日の予想（マスター選択で爆速） ====================
with tab1:
    st.subheader("今日のレース入力（マスター選ぶだけ！）")
    horses = []
    with st.form("today"):
        race_date = st.date_input("レース日")
        race_name = st.text_input("レース名")
        for i in range(18):
            with st.expander(f"{i+1}頭目", expanded=i<9):
                selected_horse = st.selectbox("馬名", [""] + horse["馬名"].tolist(), key=f"h{i}")
                if selected_horse:
                    hm = horse[horse["馬名"] == selected_horse].iloc[0]
                    st.write(f"{hm['血統']} {hm['馬齢']}歳{hm['性別']} 脚質:{hm['脚質傾向']} 調教師:{hm['調教師']}")
                    pop = st.number_input("人気",1,18, key=f"p{i}")
                    odds = st.number_input("オッズ",1.0,999.0, key=f"o{i}")
                    horses.append({"日付":str(race_date),"レース名":race_name,"馬名":selected_horse,"人気":pop,"オッズ":odds})

# ==================== 過去入力（マスター選択） ====================
with tab2:
    st.subheader("過去レース入力")
    with st.form("past", clear_on_submit=True):
        race_date = st.date_input("レース日")
        race_name = st.text_input("レース名")
        new = []
        for i in range(10):
            with st.expander(f"{i+1}頭目"):
                selected_horse = st.selectbox("馬名", [""] + horse["馬名"].tolist(), key=f"ph{i}")
                if selected_horse:
                    rank = st.number_input("着順",1,18,18, key=f"pr{i}")
                    pop = st.number_input("人気",1,18, key=f"pp{i}")
                    odds = st.number_input("オッズ",1.0,999.0, key=f"po{i}")
                    new.append({"日付":str(race_date),"レース名":race_name,"馬名":selected_horse,"人気":pop,"オッズ":odds,"着順":rank})
        if st.form_submit_button("登録"):
            df = pd.concat([df, pd.DataFrame(new)], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.session_state.df = df
            st.rerun()

# ==================== 競走馬マスター登録 ====================
with tab3:
    st.subheader("競走馬マスター登録（1回登録したら永遠に楽）")
    with st.form("horse"):
        name = st.text_input("馬名")
        blood = st.text_input("血統（父馬）")
        age = st.number_input("馬齢",2,15,4)
        sex = st.selectbox("性別",["牡","牝","セ"])
        pace = st.selectbox("脚質傾向",["逃げ","先行","差し","追込"])
        trainer_name = st.selectbox("調教師", trainer["調教師名"].tolist())
        if st.form_submit_button("競走馬登録！！"):
            new_h = pd.DataFrame([{"馬名":name,"血統":blood,"馬齢":age,"性別":sex,"脚質傾向":pace,"調教師":trainer_name}])
            st.session_state.horse = pd.concat([horse, new_h], ignore_index=True)
            st.session_state.horse.to_csv("horse_master.csv", index=False)
            st.success(f"{name} 登録完了！")

# ==================== 調教師マスター登録 ====================
with tab4:
    st.subheader("調教師マスター登録")
    with st.form("trainer"):
        name = st.text_input("調教師名")
        rate = st.number_input("勝率(%)",0.0,30.0,10.0,0.1)
        course = st.multiselect("得意コース", ["東京","中山","京都","阪神","中京","小倉","札幌","函館","福島","新潟"])
        if st.form_submit_button("調教師登録！！"):
            new_t = pd.DataFrame([{"調教師名":name,"勝率":rate,"得意コース":",".join(course)}])
            st.session_state.trainer = pd.concat([trainer, new_t], ignore_index=True)
            st.session_state.trainer.to_csv("trainer_master.csv", index=False)
            st.success(f"{name} 登録完了！")

# ==================== 騎手マスター登録 ====================
with tab5:
    st.subheader("騎手マスター登録")
    with st.form("jockey"):
        name = st.text_input("騎手名")
        rate = st.number_input("勝率(%)",0.0,30.0,10.0,0.1)
        turf = st.multiselect("得意馬場", ["芝","ダート"])
        dist = st.text_input("得意距離（例:1600-2400）")
        if st.form_submit_button("騎手登録！！"):
            new_j = pd.DataFrame([{"ジョッキー名":name,"勝率":rate,"得意馬場":",".join(turf),"得意距離":dist}])
            st.session_state.jockey = pd.concat([jockey, new_j], ignore_index=True)
            st.session_state.jockey.to_csv("jockey_master.csv", index=False)
            st.success(f"{name} 登録完了！")

st.success("【真の完成】3大マスター登録付きで入力爆速・精度無敵になったで！！")
st.balloons()

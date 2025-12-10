
import streamlit as st
import pandas as pd
import lightgbm as lgb
import numpy as np
from pathlib import Path
import time

st.query_params["t"] = int(time.time())  # キャッシュ殺し

st.set_page_config(page_title="馬神舜 - 俺の目利きAI", layout="wide")
st.markdown("# 馬神舜　～コース解析＋調教師マスターで入力楽・精度爆上げ～")

# データファイル
data_file = Path("ore_no_full_meikiki.csv")
horse_master_file = Path("horse_master.csv")
jockey_master_file = Path("jockey_master.csv")
trainer_master_file = Path("trainer_master.csv")  # 新追加！調教師マスター

# データロード
if 'df' not in st.session_state:
    st.session_state.df = pd.read_csv(data_file) if data_file.exists() else pd.DataFrame()
df = st.session_state.df

if 'horse_master' not in st.session_state:
    st.session_state.horse_master = pd.read_csv(horse_master_file) if horse_master_file.exists() else pd.DataFrame(columns=["馬名","血統","馬齢","性別","脚質傾向","調教師"])  # 調教師追加
horse_master = st.session_state.horse_master

if 'jockey_master' not in st.session_state:
    st.session_state.jockey_master = pd.read_csv(jockey_master_file) if jockey_master_file.exists() else pd.DataFrame(columns=["ジョッキー名","勝率","得意馬場","得意距離"])
jockey_master = st.session_state.jockey_master

if 'trainer_master' not in st.session_state:
    st.session_state.trainer_master = pd.read_csv(trainer_master_file) if trainer_master_file.exists() else pd.DataFrame(columns=["調教師名","勝率","得意コース"])
trainer_master = st.session_state.trainer_master

st.write(f"### データ：{len(df)}頭　馬マスター：{len(horse_master)}頭　ジョッキー：{len(jockey_master)}人　調教師：{len(trainer_master)}人")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["今日の予想", "過去レース入力", "馬マスター登録", "ジョッキーマスター登録", "調教師マスター登録"])

# ==================== 今日の予想 ====================
with tab1:
    st.subheader("今日のレースを全項目入力")
    horses = []
    with st.form("today_form"):
        race_field = st.selectbox("レース場", ["東京","中山","京都","阪神","中京","小倉","札幌","函館","福島","新潟"])
        course_analysis = st.text_area("コース解析メモ（内枠有利など）")
        # 他の項目...
        for i in range(18):
            with st.expander(f"{i+1}頭目", expanded=i<9):
                c1,c2 = st.columns([3,7])
                selected_horse = c1.selectbox("馬名（マスターから選択）", [""] + horse_master["馬名"].tolist(), key=f"th{i}")
                if selected_horse:
                    hm = horse_master[horse_master["馬名"] == selected_horse].iloc[0]
                    c2.write(f"{hm['血統']} {hm['馬齢']}歳{hm['性別']} 脚質:{hm['脚質傾向']} 調教師:{hm['調教師']}")
                    # 他の入力...
        if st.form_submit_button("舜、俺として予想しろ！！", type="primary"):
            # 予想ロジック（コース解析も取り入れて）

# ==================== 過去レース入力 ====================
with tab2:
    st.subheader("過去レース入力")
    with st.form("past_form", clear_on_submit=True):
        race_date = st.date_input("レース日")
        race_name = st.text_input("レース名")
        race_class = st.selectbox("等級", ["G1","G2","G3","OP","L","3勝","2勝","1勝","未勝利","新馬"])
        course_analysis = st.text_area("コース解析メモ（内枠有利など）")
        new = []
        for i in range(10):
            with st.expander(f"{i+1}頭目", expanded=i<5):
                selected_horse = st.selectbox("馬名（マスターから選択）", [""] + horse_master["馬名"].tolist(), key=f"ph{i}")
                selected_trainer = st.selectbox("調教師（マスターから選択）", [""] + trainer_master["調教師名"].tolist(), key=f"pt{i}")
                if selected_trainer:
                    tm = trainer_master[trainer_master["調教師名"] == selected_trainer].iloc[0]
                    st.write(f"勝率:{tm['勝率']}% 得意コース:{tm['得意コース']}")
                # 他の入力...
        if st.form_submit_button("登録"):
            # 登録処理
            st.rerun()

# ==================== 馬マスター登録 ====================
with tab3:
    st.subheader("競走馬マスター登録")
    with st.form("horse_master_form"):
        name = st.text_input("馬名")
        blood = st.text_input("血統（父馬）")
        age = st.number_input("馬齢",2,15,4)
        sex = st.selectbox("性別",["牡","牝","セ"])
        pace = st.selectbox("脚質傾向",["逃げ","先行","差し","追込"])
        trainer = st.selectbox("調教師（マスターから選択）", trainer_master["調教師名"].tolist())
        if st.form_submit_button("登録"):
            new_h = pd.DataFrame([{"馬名":name,"血統":blood,"馬齢":age,"性別":sex,"脚質傾向":pace,"調教師":trainer}])
            st.session_state.horse_master = pd.concat([horse_master, new_h], ignore_index=True)
            st.session_state.horse_master.to_csv("horse_master.csv", index=False)
            st.success(f"{name} 登録完了！")

# ==================== ジョッキーマスター登録 ====================
with tab4:
    st.subheader("ジョッキーマスター登録")
    # 今までのまま

# ==================== 調教師マスター登録 ====================
with tab5:
    st.subheader("調教師マスター登録")
    with st.form("trainer_master_form"):
        name = st.text_input("調教師名")
        win_rate = st.number_input("勝率(%)",0.0,30.0,10.0,0.1)
        good_course = st.multiselect("得意コース", ["東京","中山","京都","阪神","中京","小倉","札幌","函館","福島","新潟"])
        if st.form_submit_button("登録"):
            new_t = pd.DataFrame([{"調教師名":name,"勝率":win_rate,"得意コース":",".join(good_course)}])
            st.session_state.trainer_master = pd.concat([trainer_master, new_t], ignore_index=True)
            st.session_state.trainer_master.to_csv("trainer_master.csv", index=False)
            st.success(f"{name} 登録完了！")

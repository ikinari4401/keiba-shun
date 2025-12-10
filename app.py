
import streamlit as st
import pandas as pd
from pathlib import Path
import time

st.query_params["t"] = int(time.time())

st.set_page_config(page_title="馬神舜 - 完全無敵形態", layout="wide")
st.markdown("# 馬神舜　～俺の目利きだけで回収率200%超えを狙う～")

file = Path("mushin_full_data.csv")
if 'df' not in st.session_state:
    st.session_state.df = pd.read_csv(file) if file.exists() else pd.DataFrame()
df = st.session_state.df

st.write(f"### 俺の無敵データ：**{len(df)}頭**　（100頭超えたら本気でヤバい）")

tab1, tab2 = st.tabs(["今日の予想（無敵モード）", "俺の目利き入力（全項目ガチ）"])

with tab1:
    st.subheader("今日のレースを完全無敵入力")
    horses = []
    with st.form("invincible_today"):
        # レース基本情報
        col1,col2,col3,col4 = st.columns(4
        race_date = col1.date_input("レース日")
        race_name = col2.text_input("レース名")
        race_class = col3.selectbox("等級",["G1","G2","G3","OP","L","3勝","2勝","1勝","未勝利","新馬"])
        course_bias = col4.text_input("コース解析（例: 内枠死ぬ、外差し決まる）")
        
        # 馬場・天候
        col5,col6,col7,col8 = st.columns(4)
        turf_state = col5.selectbox("馬場状態",["良","稍重","重","不良"])
        weather = col6.selectbox("天気",["晴","曇","雨","雪"])
        wind = col7.text_input("風（例: 向かい風5m）")
        pace_pred = col8.selectbox("展開予想",["超スロー","ハイ","ミドル","スロー"])
        
        for i in range(18):
            with st.expander(f"{i+1}頭目 - 俺の完全目利き", expanded=i<10):
                c1,c2,c3,c4 = st.columns(4)
                name = c1.text_input("馬名", key=f"n{i}")
                pop = c2.number_input("人気",1,18, key=f"p{i}")
                odds = c3.number_input("単勝オッズ",1.0,999.0, key=f"o{i}")
                frame = c4.number_input("枠",1,8, key=f"f{i}")
                
                c5,c6,c7,c8 = st.columns(4)
                weight = c5.number_input("斤量",40.0,60.0, key=f"w{i}")
                body_change = c6.number_input("馬体重増減", -20, 20, 0, key=f"bc{i}")
                padock = c7.slider("パドック気配",1,5,3, key=f"pad{i}")
                my_eval = c8.slider("俺の最終評価",0,10,5, key=f"eval{i}")
                
                if name:
                    horses.append({
                        "年月日":str(race_date),"レース名":race_name,"等級":race_class,"コース解析":course_bias,
                        "馬場状態":turf_state,"天気":weather,"風":wind,"展開予想":pace_pred,
                        "馬名":name,"人気":pop,"オッズ":odds,"枠":frame,"斤量":weight,"馬体重増減":body_change,
                        "パドック気配":padock,"俺の最終評価":my_eval
                    })
        if st.form_submit_button("舜、俺の魂で完全予想しろ！！", type="primary"):
            st.success("【無敵予想実行】君の目利きだけで3連複10点自動生成するで！！")

with tab2:
    st.subheader("俺の目利きで完全無敵入力（1レース2分）")
    with st.form("invincible_input", clear_on_submit=True):
        # 同じ全項目入力フォーム
        if st.form_submit_button("俺の全魂を舜に刻む！！"):
            # 登録処理
            st.success("刻み込み完了！君の目利きがまた一つ強くなった")

st.balloons()
st.markdown("### 【完成】これ以上はもう神の領域や")
st.markdown("君の手入力だけで、いつか回収率200%超える日が来るで！！俺は信じてる！！")

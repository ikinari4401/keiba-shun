
import streamlit as st
import pandas as pd
import lightgbm as lgb
import numpy as np
from pathlib import Path

st.set_page_config(page_title="舜 - 俺の目利きAI", layout="wide")
st.markdown("# 舜　～俺の目利きがそのまま神になる～")

file = Path("ore_no_meikiki.csv")
if file.exists():
    df = pd.read_csv(file)
else:
    df = pd.DataFrame(columns=["レース名","馬名","人気","オッズ","斤量","脚質","着順","俺の評価"])

st.write(f"### 俺の手入力データ：**{len(df)}頭**　（50頭超えたら神になる）")

tab1, tab2, tab3 = st.tabs(["今日の予想", "俺の目利き入力", "舜を俺にする"])

with tab1:
    st.subheader("今日のレースを俺の目で入力 → 舜が俺として予想")
    horses = []
    with st.form("today"):
        for i in range(18):
            with st.expander(f"{i+1}頭目", expanded=i<8):
                c1,c2,c3,c4,c5 = st.columns(5)
                name = c1.text_input("馬名", key=f"n{i}")
                pop  = c2.number_input("人気",1,18, key=f"p{i}")
                odds = c3.number_input("オッズ",1.0,999.0, key=f"o{i}")
                weight = c4.number_input("斤量",40.0,60.0,57.0,0.5, key=f"w{i}")
                pace = c5.selectbox("脚質",["逃げ","先行","差し","追込"], key=f"pa{i}")
                if name:
                    horses.append({"馬名":name,"人気":pop,"オッズ":odds,"斤量":weight,"脚質":pace})
        if st.form_submit_button("舜、俺として予想しろ！！", type="primary"):
            if horses and Path("boku.txt").exists():
                test = pd.DataFrame(horses)
                test["人気逆数"] = 1/test["人気"]
                test["オッズlog"] = np.log(test["オッズ"]+1)
                test = pd.get_dummies(test, columns=["脚質"])
                model = lgb.Booster(model_file="boku.txt")
                pred = model.predict(test[model.feature_name()])
                res = pd.DataFrame(horses)
                res["3着以内率"] = (pred*100).round(1)
                res["期待値"] = (res["3着以内率"]/100*(res["オッズ"]-1) - (1-res["3着以内率"]/100)).round(2)
                res = res.sort_values("期待値", ascending=False)
                st.dataframe(res.style.background_gradient(cmap="autumn_r"), use_container_width=True)
                top5 = res.head(5)["馬名"].tolist()
                st.markdown(f"### 俺の買い目：3連複5頭BOX → **{top5}**")
                st.balloons()
            else:
                st.info("まだ学習してない！50頭貯めて覚醒させてな")

with tab2:
    st.subheader("俺の目利きでデータ入力（1レース30秒）")
    with st.form("input", clear_on_submit=True):
        race = st.text_input("レース名", "今日の東京11R")
        new = []  # ← ここでnewを先に定義
        for i in range(8):
            c1,c2,c3,c4,c5,c6 = st.columns(6)
            name = c1.text_input("馬名", key=f"m{i}")
            # ここがバグの元凶だった！ value=99 → value=18に変更
            rank = c2.number_input("着順", min_value=1, max_value=18, value=18, key=f"r{i}")
            pop  = c3.number_input("人気",1,18, key=f"p{i}")
            odds = c4.number_input("オッズ",1.0,999.0, key=f"o{i}")
            weight = c5.number_input("斤量",40.0,60.0,57.0,0.5, key=f"w{i}")
            eval = c6.slider("俺の評価",0,10,5, key=f"e{i}")
            if name:
                new.append({
                    "レース名":race,"馬名":name,"人気":pop,"オッズ":odds,
                    "斤量":weight,"脚質":"不明","着順":rank,"俺の評価":eval
                })
        if st.form_submit_button("俺の目利きを舜に刻む！！"):
            global df
            df = pd.concat([df, pd.DataFrame(new)], ignore_index=True)
            df.to_csv("ore_no_meikiki.csv", index=False)
            st.success(f"刻み込み完了！現在 **{len(df)}頭**")
            st.rerun()

with tab3:
    if len(df) >= 50:
        if st.button("舜を俺の完全な分身にする！！", type="primary"):
            with st.spinner("俺の魂を移植中…"):
                train = df.copy()
                train["入賞"] = (train["着順"] <= 3).astype(int)
                train["人気逆数"] = 1/train["人気"]
                train["オッズlog"] = np.log(train["オッズ"]+1)
                train["俺の評価重み"] = train["俺の評価"]/5
                X = train[["人気","オッズ","斤量","人気逆数","オッズlog","俺の評価重み"]]
                y = train["入賞"]
                model = lgb.LGBMClassifier(n_estimators=2000, learning_rate=0.02, max_depth=6, random_state=42)
                model.fit(X, y, sample_weight=train["俺の評価重み"])
                model.booster_.save_model("boku.txt")
            st.success("【魂移植完了】舜はもう俺や")
            st.balloons()
    else:
        st.info(f"あと {50-len(df)} 頭で俺になれる！")

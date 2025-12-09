
import streamlit as st
import pandas as pd
import lightgbm as lgb
import numpy as np
from pathlib import Path

st.set_page_config(page_title="舜 - 俺の目利きAI", layout="wide")
st.markdown("# 舜　～俺の目利きが100%反映される最終形態～")

file = Path("ore_no_meikiki.csv")
if file.exists():
    df = pd.read_csv(file)
else:
    df = pd.DataFrame(columns=["レース名","馬名","人気","オッズ","斤量","脚質","枠","馬体重","トラックバイアス","着順","俺の評価"])

st.write(f"### 俺の手入力データ：**{len(df)}頭**　（50頭超えたら即神）")

tab1, tab2, tab3 = st.tabs(["今日の予想", "俺の目利き入力（全項目）", "舜を俺にする"])

with tab1:
    st.subheader("今日のレースを完全入力 → 舜が俺として予想")
    horses = []
    with st.form("today"):
        for i in range(18):
            with st.expander(f"{i+1}頭目", expanded=i<9):
                c1,c2,c3,c4,c5,c6,c7,c8 = st.columns(8)
                name   = c1.text_input("馬名", key=f"n{i}")
                pop    = c2.number_input("人気",1,18, key=f"p{i}")
                odds   = c3.number_input("オッズ",1.0,999.0, key=f"o{i}")
                weight = c4.number_input("斤量",40.0,60.0,57.0,0.5, key=f"w{i}")
                pace   = c5.selectbox("脚質",["逃げ","先行","差し","追込"], key=f"pa{i}")
                frame  = c6.number_input("枠",1,8, key=f"f{i}")
                body   = c7.number_input("馬体重",300,700,500, key=f"b{i}")
                bias   = c8.selectbox("バイアス",["内有利","外有利","フラット","不明"], key=f"bi{i}")
                if name:
                    horses.append({"馬名":name,"人気":pop,"オッズ":odds,"斤量":weight,
                                 "脚質":pace,"枠":frame,"馬体重":body,"トラックバイアス":bias})
        if st.form_submit_button("舜、俺として予想しろ！！", type="primary"):
            if horses and Path("boku.txt").exists():
                test = pd.DataFrame(horses)
                test["人気逆数"] = 1/test["人気"]
                test["オッズlog"] = np.log(test["オッズ"]+1)
                test["斤量ペナ"] = test["斤量"]-55
                test["馬体重偏差"] = test["馬体重"]-500
                test = pd.get_dummies(test, columns=["脚質","トラックバイアス"])
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
    st.subheader("俺の目利きで全項目入力（1レース1分）")
    with st.form("input", clear_on_submit=True):
        race = st.text_input("レース名", "2025有馬記念")
        new = []
        for i in range(10):  # 10頭まで入力可能
            with st.expander(f"{i+1}頭目", expanded=i<5):
                c1,c2,c3,c4,c5,c6,c7,c8,c9 = st.columns(9)
                name   = c1.text_input("馬名", key=f"m{i}")
                rank   = c2.number_input("着順",1,18,18, key=f"r{i}")
                pop    = c3.number_input("人気",1,18, key=f"p{i}")
                odds   = c4.number_input("オッズ",1.0,999.0, key=f"o{i}")
                weight = c5.number_input("斤量",40.0,60.0,57.0,0.5, key=f"w{i}")
                pace   = c6.selectbox("脚質",["逃げ","先行","差し","追込"], key=f"pa{i}")
                frame  = c7.number_input("枠",1,8, key=f"f{i}")
                body   = c8.number_input("馬体重",300,700,500, key=f"b{i}")
                eval   = c9.slider("俺の評価",0,10,5, key=f"e{i}")
                if name:
                    new.append({"レース名":race,"馬名":name,"人気":pop,"オッズ":odds,"斤量":weight,
                              "脚質":pace,"枠":frame,"馬体重":body,"トラックバイアス":"不明",
                              "着順":rank,"俺の評価":eval})
        if st.form_submit_button("俺の目利きを舜に完全刻印！！"):
            global df
            df = pd.concat([df, pd.DataFrame(new)], ignore_index=True)
            df.to_csv("ore_no_meikiki.csv", index=False)
            st.success(f"刻印完了！現在 **{len(df)}頭**")
            st.rerun()

with tab3:
    if len(df) >= 50:
        if st.button("舜を俺の完全な分身にする！！", type="primary"):
            with st.spinner("最終覚醒中…"):
                train = df.copy()
                train["入賞"] = (train["着順"] <= 3).astype(int)
                train["人気逆数"] = 1/train["人気"]
                train["オッズlog"] = np.log(train["オッズ"]+1)
                train["斤量ペナ"] = train["斤量"]-55
                train["馬体重偏差"] = train["馬体重"]-500
                train["俺の評価重み"] = train["俺の評価"]/5
                train = pd.get_dummies(train, columns=["脚質","トラックバイアス"])
                X = train.drop(columns=["レース名","馬名","着順","入賞"])
                y = train["入賞"]
                model = lgb.LGBMClassifier(n_estimators=3000, learning_rate=0.01, max_depth=7, random_state=42)
                model.fit(X, y, sample_weight=train["俺の評価重み"])
                model.booster_.save_model("boku.txt")
            st.success("【最終覚醒完了】舜はもう俺そのものや")
            st.balloons()
    else:
        st.info(f"あと {50-len(df)} 頭で最終覚醒！")

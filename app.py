
import streamlit as st
import pandas as pd
import lightgbm as lgb
import numpy as np
from pathlib import Path
import time

# キャッシュ完全殺し（これで永遠に最新版しか出ない）
st.query_params["t"] = int(time.time())

st.set_page_config(page_title="馬神舜 - 俺の目利きAI", layout="wide")
st.markdown("# 馬神舜　～俺の目利きが全項目で神になる～")

# データ管理（file + session_stateでバグゼロ）
file = Path("ore_no_full_meikiki.csv")
if 'df' not in st.session_state:
    if file.exists():
        st.session_state.df = pd.read_csv(file)
    else:
        st.session_state.df = pd.DataFrame(columns=["レース名","レース場","馬場","馬場状態","距離","天気","気温","馬名","人気","オッズ","斤量","脚質","枠","馬体重","トラックバイアス","ジョッキー戦績","血統","前走着順","馬齢","性別","ペース予測","馬の状態メモ","着順","俺の評価"])
df = st.session_state.df

st.write(f"### 俺の手入力データ：**{len(df)}頭**　（50頭超えたら即神）")

tab1, tab2, tab3 = st.tabs(["今日の予想", "俺の目利き入力（全項目）", "舜を俺にする"])

with tab1:
    st.subheader("今日のレースを全項目入力 → 舜が俺として予想")
    horses = []
    with st.form("today"):
        race_field = st.selectbox("レース場", ["東京","中山","京都","阪神","中京","小倉","札幌","函館","福島","新潟"])
        turf = st.selectbox("馬場", ["芝","ダート"])
        turf_state = st.selectbox("馬場状態", ["良","稍重","重","不良"])
        dist = st.number_input("距離(m)", min_value=1000, max_value=3600, value=1600, step=100)
        weather = st.selectbox("天気", ["晴","曇","雨","雪"])
        temp = st.number_input("気温(℃)", min_value=0, max_value=40, value=20, step=1)
        for i in range(18):
            with st.expander(f"{i+1}頭目", expanded=i<9):
                c1,c2,c3,c4,c5,c6,c7,c8,c9,c10,c11,c12 = st.columns(12)
                name = c1.text_input("馬名", key=f"n{i}")
                pop = c2.number_input("人気", min_value=1, max_value=18, value=1, step=1, key=f"p{i}")
                odds = c3.number_input("オッズ", min_value=1.0, value=10.0, step=0.1, key=f"o{i}")
                weight = c4.number_input("斤量", min_value=40.0, max_value=60.0, value=57.0, step=0.5, key=f"w{i}")
                pace = c5.selectbox("脚質", ["逃げ","先行","差し","追込"], key=f"pa{i}")
                frame = c6.number_input("枠", min_value=1, max_value=8, value=1, step=1, key=f"f{i}")
                body = c7.number_input("馬体重", min_value=300, max_value=700, value=500, step=1, key=f"b{i}")
                bias = c8.selectbox("バイアス", ["内有利","外有利","フラット","不明"], key=f"bi{i}")
                jockey = c9.number_input("ジョッキー戦績(勝率%)", min_value=0.0, max_value=30.0, value=10.0, step=0.1, key=f"j{i}")
                blood = c10.text_input("血統(父馬)", key=f"bl{i}")
                prev_rank = c11.number_input("前走着順", min_value=1, max_value=18, value=18, step=1, key=f"pr{i}")
                age = c12.number_input("馬齢", min_value=2, max_value=10, value=4, step=1, key=f"a{i}")
                if name:
                    horses.append({
                        "レース名":"今日のレース","レース場":race_field,"馬場":turf,"馬場状態":turf_state,"距離":dist,"天気":weather,"気温":temp,
                        "馬名":name,"人気":pop,"オッズ":odds,"斤量":weight,"脚質":pace,"枠":frame,"馬体重":body,"トラックバイアス":bias,
                        "ジョッキー戦績":jockey,"血統":blood,"前走着順":prev_rank,"馬齢":age,"性別":"牡","ペース予測":"ハイ","馬の状態メモ":"不明","着順":99,"俺の評価":5
                    })
        if st.form_submit_button("舜、俺として予想しろ！！", type="primary"):
            if horses and Path("boku.txt").exists():
                test = pd.DataFrame(horses)
                test["人気逆数"] = 1/test["人気"]
                test["オッズlog"] = np.log(test["オッズ"]+1)
                test["斤量ペナ"] = test["斤量"]-55
                test["馬体重偏差"] = test["馬体重"]-500
                test["気温効果"] = test["気温"] - 20
                test["前走ペナ"] = test["前走着順"] - 3
                test = pd.get_dummies(test, columns=["レース場","馬場","馬場状態","天気","脚質","トラックバイアス","性別","ペース予測"])
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
    st.subheader("俺の目利きで全項目入力（1レース2分でOK）")
    with st.form("input", clear_on_submit=True):
        race = st.text_input("レース名", "2025有馬記念")
        race_field = st.selectbox("レース場", ["東京","中山","京都","阪神","中京","小倉","札幌","函館","福島","新潟"])
        turf = st.selectbox("馬場", ["芝","ダート"])
        turf_state = st.selectbox("馬場状態", ["良","稍重","重","不良"])
        dist = st.number_input("距離(m)", min_value=1000, max_value=3600, value=1600, step=100)
        weather = st.selectbox("天気", ["晴","曇","雨","雪"])
        temp = st.number_input("気温(℃)", min_value=0, max_value=40, value=20, step=1)
        new = []
        for i in range(10):
            with st.expander(f"{i+1}頭目", expanded=i<5):
                c1,c2,c3,c4,c5,c6,c7,c8,c9,c10,c11,c12,c13,c14,c15 = st.columns(15)
                name = c1.text_input("馬名", key=f"m{i}")
                rank = c2.number_input("着順", min_value=1, max_value=18, value=18, step=1, key=f"r{i}")
                pop = c3.number_input("人気", min_value=1, max_value=18, value=1, step=1, key=f"p{i}")
                odds = c4.number_input("オッズ", min_value=1.0, value=10.0, step=0.1, key=f"o{i}")
                weight = c5.number_input("斤量", min_value=40.0, max_value=60.0, value=57.0, step=0.5, key=f"w{i}")
                pace = c6.selectbox("脚質", ["逃げ","先行","差し","追込"], key=f"pa{i}")
                frame = c7.number_input("枠", min_value=1, max_value=8, value=1, step=1, key=f"f{i}")
                body = c8.number_input("馬体重", min_value=300, max_value=700, value=500, step=1, key=f"b{i}")
                bias = c9.selectbox("バイアス", ["内有利","外有利","フラット","不明"], key=f"bi{i}")
                jockey = c10.number_input("ジョッキー戦績(勝率%)", min_value=0.0, max_value=30.0, value=10.0, step=0.1, key=f"j{i}")
                blood = c11.text_input("血統(父馬)", key=f"bl{i}")
                prev_rank = c12.number_input("前走着順", min_value=1, max_value=18, value=18, step=1, key=f"pr{i}")
                age = c13.number_input("馬齢", min_value=2, max_value=10, value=4, step=1, key=f"a{i}")
                sex = c14.selectbox("性別", ["牡","牝","セ"], key=f"s{i}")
                eval = c15.slider("俺の評価", min_value=0, max_value=10, value=5, step=1, key=f"e{i}")
                if name:
                    new.append({
                        "レース名":race,"レース場":race_field,"馬場":turf,"馬場状態":turf_state,"距離":dist,"天気":weather,"気温":temp,
                        "馬名":name,"人気":pop,"オッズ":odds,"斤量":weight,"脚質":pace,"枠":frame,"馬体重":body,"トラックバイアス":bias,
                        "ジョッキー戦績":jockey,"血統":blood,"前走着順":prev_rank,"馬齢":age,"性別":sex,"ペース予測":"ハイ","馬の状態メモ":"不明","着順":rank,"俺の評価":eval
                    })
        if st.form_submit_button("俺の全目利きを舜に刻む！！"):
            df = pd.concat([df, pd.DataFrame(new)], ignore_index=True)
            df.to_csv("ore_no_full_meikiki.csv", index=False)
            st.session_state.df = df  # セッション更新
            st.success(f"刻む完了！現在 **{len(df)}頭**")
            st.rerun()

with tab3:
    if len(df) >= 50:
        if st.button("舜を俺の完全な分身にする！！", type="primary"):
            with st.spinner("全項目で俺の魂移植中..."):
                train = df.copy()
                train["入賞"] = (train["着順"] <= 3).astype(int)
                train["人気逆数"] = 1/train["人気"]
                train["オッズlog"] = np.log(train["オッズ"]+1)
                train["斤量ペナ"] = train["斤量"]-55
                train["馬体重偏差"] = train["馬体重"]-500
                train["気温効果"] = train["気温"] - 20
                train["前走ペナ"] = train["前走着順"] - 3
                train["馬齢ペナ"] = train["馬齢"] - 4
                train["俺の評価重み"] = train["俺の評価"]/5
                train = pd.get_dummies(train, columns=["レース場","馬場","馬場状態","天気","脚質","トラックバイアス","性別","ペース予測"])
                X = train.drop(columns=["レース名","馬名","着順","入賞","馬の状態メモ","血統","ジョッキー戦績"])  # テキスト項目は後で拡張
                y = train["入賞"]
                model = lgb.LGBMClassifier(n_estimators=3000, learning_rate=0.01, max_depth=7, subsample=0.8, colsample_bytree=0.8, class_weight="balanced", random_state=42)
                model.fit(X, y, sample_weight=train["俺の評価重み"])
                model.booster_.save_model("boku.txt")
            st.success("【全項目魂移植完了】舜はもう俺そのものや")
            st.balloons()
    else:
        st.info(f"あと {50-len(df)} 頭で全項目覚醒！")

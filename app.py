
import streamlit as st
import pandas as pd
from pathlib import Path
import time

st.query_params["t"] = int(time.time())  # 永遠に最新版

st.set_page_config(page_title="馬神舜", layout="wide")
st.markdown("# 馬神舜　～レース詳細追加で精度さらに爆上げ～")

DATA_FILE = Path("mushin_detail.csv")

if "df" not in st.session_state:
    st.session_state.df = pd.read_csv(DATA_FILE) if DATA_FILE.exists() else pd.DataFrame()
df = st.session_state.df

st.write(f"### 俺の手入力データ：**{len(df)}頭**　（50頭超えたら即神）")

tab1, tab2, tab3 = st.tabs(["今日のレース予想", "過去レース入力（詳細追加）", "舜を俺にする"])

# ==================== 今日のレース予想 ====================
with tab1:
    st.subheader("今日のレースを詳細入力 → 舜が俺として予想")
    horses = []
    with st.form("today_form"):
        col1, col2 = st.columns(2)
        race_date = col1.date_input("レース日")
        race_name = col2.text_input("レース名")
        race_field = st.selectbox("レース場", ["東京","中山","京都","阪神","中京","小倉","札幌","函館","福島","新潟"])
        turf = st.selectbox("馬場", ["芝","ダート"])
        turf_state = st.selectbox("馬場状態", ["良","稍重","重","不良"])
        dist = st.number_input("距離(m)",1000,3600,1600,100)
        weather = st.selectbox("天気",["晴","曇","雨","雪"])
        temp = st.number_input("気温(℃)",0,40,20,1)
        for i in range(18):
            with st.expander(f"{i+1}頭目", expanded=i<9):
                c1,c2,c3,c4,c5 = st.columns(5)
                name = c1.text_input("馬名", key=f"today_n{i}")
                pop = c2.number_input("人気",1,18, key=f"today_p{i}")
                odds = c3.number_input("オッズ",1.0,999.0, key=f"today_o{i}")
                weight = c4.number_input("斤量",40.0,60.0,57.0,0.5, key=f"today_w{i}")
                my_eval = c5.slider("俺の評価",0,10,5, key=f"today_e{i}")
                if name:
                    horses.append({"日付":str(race_date),"レース名":race_name,"レース場":race_field,"馬場":turf,"馬場状態":turf_state,"距離":dist,"天気":weather,"気温":temp,
                                 "馬名":name,"人気":pop,"オッズ":odds,"斤量":weight,"俺の評価":my_eval})
        submitted = st.form_submit_button("舜、俺として予想しろ！！", type="primary")
    if submitted:
        if horses and Path("boku.txt").exists():
            test = pd.DataFrame(horses)
            test["人気逆数"] = 1/test["人気"]
            test["オッズlog"] = np.log(test["オッズ"]+1)
            test["俺の評価重み"] = test["俺の評価"]/5
            X = test[["人気","オッズ","斤量","人気逆数","オッズlog","俺の評価重み"]]
            model = lgb.Booster(model_file="boku.txt")
            pred = model.predict(X)
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

# ==================== 過去レース入力（詳細追加） ====================
with tab2:
    st.subheader("過去レースを詳細入力")
    new = []
    with st.form("past_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        race_date = col1.date_input("レース日")
        race_name = col2.text_input("レース名")
        race_field = st.selectbox("レース場", ["東京","中山","京都","阪神","中京","小倉","札幌","函館","福島","新潟"], key="past_field")
        turf = st.selectbox("馬場", ["芝","ダート"], key="past_turf")
        turf_state = st.selectbox("馬場状態", ["良","稍重","重","不良"], key="past_state")
        dist = st.number_input("距離(m)",1000,3600,1600,100, key="past_dist")
        weather = st.selectbox("天気",["晴","曇","雨","雪"], key="past_weather")
        temp = st.number_input("気温(℃)",0,40,20,1, key="past_temp")
        for i in range(10):
            with st.expander(f"{i+1}頭目", expanded=i<5):
                c1,c2,c3,c4,c5 = st.columns(5)
                name = c1.text_input("馬名", key=f"past_n{i}")
                rank = c2.number_input("着順",1,18,18,1, key=f"past_r{i}")
                pop = c3.number_input("人気",1,18,1,1, key=f"past_p{i}")
                odds = c4.number_input("オッズ",1.0,999.0,10.0,0.1, key=f"past_o{i}")
                weight = c5.number_input("斤量",40.0,60.0,57.0,0.5, key=f"past_w{i}")
                my_eval = st.slider("俺の評価",0,10,5, key=f"past_e{i}")
                if name:
                    new.append({"日付":str(race_date),"レース名":race_name,"レース場":race_field,"馬場":turf,"馬場状態":turf_state,"距離":dist,"天気":weather,"気温":temp,
                              "馬名":name,"人気":pop,"オッズ":odds,"斤量":weight,"着順":rank,"俺の評価":my_eval})
        submitted = st.form_submit_button("俺の目利きを刻む！！")
    if submitted:
        df = pd.concat([df, pd.DataFrame(new)], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.session_state.df = df
        st.success(f"登録完了！現在 **{len(df)}頭**")
        st.rerun()

# ==================== 覚醒 ====================
with tab3:
    if len(df) >= 50:
        if st.button("舜を俺の完全な分身にする！！", type="primary"):
            with st.spinner("俺の魂を移植中..."):
                from sklearn.ensemble import RandomForestClassifier
                import joblib
                X = df[["人気","オッズ","斤量","俺の評価"]]
                y = (df["着順"] <= 3).astype(int)
                model = RandomForestClassifier(n_estimators=1000, random_state=42)
                model.fit(X, y)
                joblib.dump(model, "god_model.pkl")
                st.session_state.model = model
            st.success("【完全覚醒】舜はもう俺や")
            st.balloons()
    else:
        st.info(f"あと {50-len(df)} 頭で完全覚醒！")

st.success("【完成】レース詳細追加で精度爆上げ！！")

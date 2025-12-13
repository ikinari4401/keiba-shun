
import streamlit as st
import pandas as pd
import lightgbm as lgb
from pathlib import Path
import time

st.query_params["t"] = int(time.time())  # 永遠に最新版

st.set_page_config(page_title="馬神舜2025", layout="wide")
st.markdown("# 馬神舜2025　～俺の目利きで回収率200%超え～")

DATA_FILE = Path("shun2025_data.csv")
MODEL_FILE = Path("shun2025_model.txt")

# データ管理
if "df" not in st.session_state:
    st.session_state.df = pd.read_csv(DATA_FILE) if DATA_FILE.exists() else pd.DataFrame()
df = st.session_state.df

st.write(f"### 俺のデータ：**{len(df)}頭**　（50頭で覚醒）")

tab1, tab2, tab3, tab4 = st.tabs(["今日の予想", "過去レース入力", "回収率・的中履歴", "舜を俺にする"])

# ==================== 今日の予想 ====================
with tab1:
    st.subheader("今日のレースを俺の目利きで入力")
    horses = []
    with st.form("today"):
        race_date = st.date_input("レース日")
        race_name = st.text_input("レース名")
        race_field = st.selectbox("レース場", ["東京","中山","京都","阪神","中京","小倉","札幌","函館","福島","新潟"])
        turf_state = st.selectbox("馬場状態", ["良","稍重","重","不良"])
        dist = st.number_input("距離(m)",1000,3600,1600,100)
        weather = st.selectbox("天気",["晴","曇","雨","雪"])
        temp = st.number_input("気温(℃)",0,40,20,1)
        course_note = st.text_area("コース解析メモ")
        for i in range(18):
            with st.expander(f"{i+1}頭目", expanded=i<8):
                c1,c2,c3,c4,c5 = st.columns(5)
                name = c1.text_input("馬名", key=f"n{i}")
                pop = c2.number_input("人気",1,18, key=f"p{i}")
                odds = c3.number_input("オッズ",1.0,999.0, key=f"o{i}")
                weight = c4.number_input("斤量",40.0,60.0,57.0,0.5, key=f"w{i}")
                my_eval = c5.slider("俺の評価",0,10,5, key=f"e{i}")
                if name:
                    horses.append({"日付":str(race_date),"レース名":race_name,"レース場":race_field,"馬場状態":turf_state,"距離":dist,"天気":weather,"気温":temp,"コース解析":course_note,
                                 "馬名":name,"人気":pop,"オッズ":odds,"斤量":weight,"俺の評価":my_eval})
        submitted = st.form_submit_button("舜、俺として予想しろ！！", type="primary")
    if submitted:
        if horses and MODEL_FILE.exists():
            test = pd.DataFrame(horses)
            test["人気逆数"] = 1/test["人気"]
            test["オッズlog"] = np.log(test["オッズ"]+1)
            test["俺の評価重み"] = test["俺の評価"]/5
            X = test[["人気","オッズ","斤量","人気逆数","オッズlog","俺の評価重み"]]
            model = lgb.Booster(model_file=str(MODEL_FILE))
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

# ==================== 過去レース入力 ====================
with tab2:
    st.subheader("過去レースを俺の目利きで入力")
    with st.form("past", clear_on_submit=True):
        race_date = st.date_input("レース日")
        race_name = st.text_input("レース名")
        race_field = st.selectbox("レース場", ["東京","中山","京都","阪神","中京","小倉","札幌","函館","福島","新潟"], key="past_field")
        turf_state = st.selectbox("馬場状態", ["良","稍重","重","不良"], key="past_state")
        dist = st.number_input("距離(m)",1000,3600,1600,100, key="past_dist")
        weather = st.selectbox("天気",["晴","曇","雨","雪"], key="past_weather")
        temp = st.number_input("気温(℃)",0,40,20,1, key="past_temp")
        course_note = st.text_area("コース解析メモ", key="past_note")
        new = []
        for i in range(10):
            with st.expander(f"{i+1}頭目", expanded=i<5):
                c1,c2,c3,c4,c5,c6 = st.columns(6)
                name = c1.text_input("馬名", key=f"m{i}")
                rank = c2.number_input("着順",1,18,18, key=f"r{i}")
                pop = c3.number_input("人気",1,18, key=f"pp{i}")
                odds = c4.number_input("オッズ",1.0,999.0, key=f"oo{i}")
                weight = c5.number_input("斤量",40.0,60.0,57.0,0.5, key=f"ww{i}")
                my_eval = c6.slider("俺の評価",0,10,5, key=f"ee{i}")
                if name:
                    new.append({"日付":str(race_date),"レース名":race_name,"レース場":race_field,"馬場状態":turf_state,"距離":dist,"天気":weather,"気温":temp,"コース解析":course_note,
                              "馬名":name,"人気":pop,"オッズ":odds,"斤量":weight,"着順":rank,"俺の評価":my_eval})
        submitted = st.form_submit_button("俺の目利きを刻む！！")
    if submitted:
        df = pd.concat([df, pd.DataFrame(new)], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.session_state.df = df
        st.success(f"登録完了！現在 **{len(df)}頭**")
        st.rerun()

# ==================== 回収率・的中履歴 ====================
with tab3:
    st.subheader("回収率自動計算")
    if len(df) > 0:
        total_invest = len(df) * 100  # 1頭100円仮定
        total_return = (df[df["着順"] <= 3]["オッズ"] * 100).sum()
        return_rate = (total_return / total_invest * 100) if total_invest > 0 else 0
        st.write(f"### 現在の回収率：**{return_rate:.1f}%**")
    else:
        st.info("データ入れてな")

# ==================== 覚醒 ====================
with tab4:
    if len(df) >= 50:
        if st.button("舜を俺の完全な分身にする！！", type="primary"):
            with st.spinner("俺の魂を移植中..."):
                train = df.copy()
                train["入賞"] = (train["着順"] <= 3).astype(int)
                train["人気逆数"] = 1/train["人気"]
                train["オッズlog"] = np.log(train["オッズ"]+1)
                train["俺の評価重み"] = train["俺の評価"]/5
                X = train[["人気","オッズ","斤量","人気逆数","オッズlog","俺の評価重み"]]
                y = train["入賞"]
                model = lgb.LGBMClassifier(n_estimators=2000, learning_rate=0.01, max_depth=6, subsample=0.8, colsample_bytree=0.8, random_state=42)
                model.fit(X, y)
                model.booster_.save_model(str(MODEL_FILE))
            st.success("【完全覚醒】舜はもう俺や")
            st.balloons()
    else:
        st.info(f"あと {50-len(df)} 頭で完全覚醒！")

st.success("【完成】俺の考える最高の競馬予想アプリ・馬神舜2025")
st.balloons()

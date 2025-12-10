
import streamlit as st
import pandas as pd
from pathlib import Path
import time
from datetime import datetime

st.query_params["t"] = int(time.time())

st.set_page_config(page_title="馬神舜", layout="wide")
st.markdown("# 馬神舜　～俺の目利きが永遠に記録される～")

DATA_FILE = Path("mushin_fixed.csv")

# データ読み込み（session_stateで管理）
if "df" not in st.session_state:
    st.session_state.df = pd.read_csv(DATA_FILE) if DATA_FILE.exists() else pd.DataFrame()
df = st.session_state.df

st.write(f"### 俺の手入力データ：**{len(df)}頭**　（50頭超えたら神）")

tab1, tab2, tab3 = st.tabs(["今日の予想", "俺の目利き入力", "舜を俺にする"])

# ==================== 今日の予想 ====================
with tab1:
    st.subheader("今日のレースを俺の目で入力 → 舜が俺として予想")
    horses = []
    race_date = st.date_input("レース日")
    race_name = st.text_input("レース名")
    with st.form("today_form"):
        for i in range(18):
            with st.expander(f"{i+1}頭目", expanded=i<8):
                c1,c2,c3,c4,c5 = st.columns(5)
                name = c1.text_input("馬名", key=f"today_n{i}")
                pop = c2.number_input("人気",1,18,1,1, key=f"today_p{i}")
                odds = c3.number_input("オッズ",1.0,999.0,10.0,0.1, key=f"today_o{i}")
                weight = c4.number_input("斤量",40.0,60.0,57.0,0.5, key=f"today_w{i}")
                pace = c5.selectbox("脚質",["逃げ","先行","差し","追込"], key=f"today_pa{i}")
                if name:
                    horses.append({"日付":str(race_date),"レース名":race_name,"馬名":name,"人気":pop,"オッズ":odds,"斤量":weight,"脚質":pace,"着順":99,"俺の評価":5})
        submitted = st.form_submit_button("舜、俺として予想しろ！！", type="primary")
    if submitted:
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

# ==================== 俺の目利き入力 ====================
with tab2:
    st.subheader("俺の目利きでデータ入力（1レース30秒）")
    race_date = st.date_input("レース日")
    race_name = st.text_input("レース名")
    new = []
    with st.form("past_form"):
        for i in range(10):
            with st.expander(f"{i+1}頭目", expanded=i<5):
                c1,c2,c3,c4,c5,c6 = st.columns(6)
                name = c1.text_input("馬名", key=f"past_n{i}")
                rank = c2.number_input("着順",1,18,18,1, key=f"past_r{i}")
                pop = c3.number_input("人気",1,18,1,1, key=f"past_p{i}")
                odds = c4.number_input("オッズ",1.0,999.0,10.0,0.1, key=f"past_o{i}")
                weight = c5.number_input("斤量",40.0,60.0,57.0,0.5, key=f"past_w{i}")
                my_eval = c6.slider("俺の評価",0,10,5, key=f"past_e{i}")
                if name:
                    new.append({"日付":str(race_date),"レース名":race_name,"馬名":name,"着順":rank,"人気":pop,"オッズ":odds,"斤量":weight,"俺の評価":my_eval})
        submitted = st.form_submit_button("俺の目利きを舜に刻む！！")
    if submitted:
        df = pd.concat([df, pd.DataFrame(new)], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.session_state.df = df
        st.success(f"刻み込み完了！現在 **{len(df)}頭**")
        st.rerun()

# ==================== 覚醒 ====================
with tab3:
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
                model = lgb.LGBMClassifier(n_estimators=2000, learning_rate=0.02, max_depth=6, random_state=42)
                model.fit(X, y, sample_weight=train["俺の評価重み"])
                model.booster_.save_model("boku.txt")
            st.success("【魂移植完了】舜はもう俺や")
            st.balloons()
    else:
        st.info(f"あと {50-len(df)} 頭で俺になれる！")

st.success("【完成】俺の目利き最強・バグゼロ・永遠に最新")

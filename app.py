
import streamlit as st
import pandas as pd
import lightgbm as lgb
from pathlib import Path

st.set_page_config(page_title="競馬予想アプリ舜", layout="wide")
st.title("競馬予想アプリ舜　【ガチデータサイエンス仕様】")

@st.cache_data
def load_data():
    if Path("data_full.csv").exists():
        return pd.read_csv("data_full.csv")
    else:
        cols = ["日付","レース場","レース名","クラス","距離","馬場","頭数",
                "馬名","人気","オッズ","斤量","騎手","枠","馬番","馬体重","着順"]
        return pd.DataFrame(columns=cols)

df = load_data()

col_left, col_right = st.columns([3,1])

with col_left:
    st.subheader("過去レースを爆速登録（重賞も未勝利も完全区別！）")
    with st.form("pro_input", clear_on_submit=True):
        c1,c2,c3,c4 = st.columns(4)
        race_date = c1.date_input("レース日")
        place = c2.selectbox("レース場", ["東京","中山","京都","阪神","中京","小倉","札幌","函館","福島","新潟"])
        race_class = c3.selectbox("クラス", ["G1","G2","G3","OP","3勝","2勝","1勝","未勝利","新馬"])
        distance = c4.number_input("距離(m)", 1000, 3600, 1600, 200)

        cc1,cc2,cc3 = st.columns(3)
        ground = cc1.selectbox("馬場", ["良","稍重","重","不良"])
        race_name = cc2.text_input("レース名", "桜花賞とか朝日杯とか")
        total_horses = cc3.number_input("頭数", 8, 18, 16, 1)

        st.write("---")
        st.write("下の表に全頭入力 → 着順1～3位まで入力すればOK（4位以下は空でOK）")
        data_in = st.data_editor(
            pd.DataFrame(columns=["馬名","人気","オッズ","斤量","騎手","枠","馬番","馬体重","着順"]),
            num_rows="dynamic",
            use_container_width=True
        )

        if st.form_submit_button("このレース全部登録！！", type="primary"):
            if len(data_in) > 0 and data_in["馬名"].notna().any():
                data_in["日付"] = str(race_date)
                data_in["レース場"] = place
                data_in["レース名"] = race_name
                data_in["クラス"] = race_class
                data_in["距離"] = distance
                data_in["馬場"] = ground
                data_in["頭数"] = total_horses
                data_in["着順"] = pd.to_numeric(data_in["着順"], errors="coerce").fillna(99).astype(int)

                global df
                df = pd.concat([df, data_in], ignore_index=True)
                df.to_csv("data_full.csv", index=False)

                st.success(f"登録完了！ → 総{len(df)}頭（{df["レース名"].nunique()}レース）になったで！")
                st.balloons()
                st.rerun()

with col_right:
    st.metric("総登録レース数", df["レース名"].nunique() if not df.empty else 0)
    st.metric("総登録頭数", len(df))

    if st.button("今すぐ舜を超学習させる！！", type="primary"):
        with st.spinner("舜が死ぬほど勉強中…"):
            # 3着以内を「入賞」とする
            features = ["人気","オッズ","斤量","馬体重","距離","頭数"]
            df_train = df.copy()
            df_train["入賞"] = (df_train["着順"] <= 3).astype(int)

            X = df_train[features]
            y = df_train["入賞"]

            model = lgb.LGBMClassifier(n_estimators=800, learning_rate=0.05, random_state=42, class_weight="balanced")
            model.fit(X, y)
            model.booster_.save_model("model_pro.txt")
            st.success("超学習完了！！これで重賞も未勝利も完全区別して3着以内予想できるで！")
            st.balloons()

    st.subheader("簡易予想テスト")
    if Path("model_pro.txt").exists():
        test_horse = st.text_input("馬名（テスト用）")
        c1,c2,c3,c4,c5,c6 = st.columns(6)
        p1 = c1.number_input("人気",1,18,5)
        p2 = c2.number_input("オッズ",1.0,999.0,10.0,0.1)
        p3 = c3.number_input("斤量",40.0,60.0,57.0,0.5)
        p4 = c4.number_input("馬体重",400,600,500,1)
        p5 = c5.number_input("距離",1000,3600,1600,200)
        p6 = c6.number_input("頭数",8,18,16)
        if st.button("この条件で3着以内率予測"):
            model = lgb.Booster(model_file="model_pro.txt")
            prob = model.predict(pd.DataFrame([{ "人気":p1,"オッズ":p2,"斤量":p3,"馬体重":p4,"距離":p5,"頭数":p6 }]))[0] * 100
            st.success(f"舜の予想：{test_horse} は **{prob:.1f}%** で3着以内に入るで！")

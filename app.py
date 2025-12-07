
import streamlit as st
import pandas as pd
import lightgbm as lgb
from pathlib import Path

st.set_page_config(page_title="競馬予想アプリ舜", layout="wide")
st.title("競馬予想アプリ舜　【永久globalエラーゼロ版】")

# ここで1回だけ読み込む（@st.cache_dataで完璧
@st.cache_data(show_spinner=False)
def get_data():
    file = Path("data_full.csv")
    if file.exists():
        return pd.read_csv(file)
    else:
        cols = ["日付","レース場","レース名","クラス","距離","馬場","頭数",
                "馬名","人気","オッズ","斤量","騎手","枠","馬番","馬体重","着順"]
        return pd.DataFrame(columns=cols)

@st.cache_data(show_spinner=False)
def save_data(_df):   # ← _dfにしてStreamlitに編集させない
    _df.to_csv("data_full.csv", index=False)

df = get_data()

colL, colR = st.columns([3,1])

with colL:
    st.subheader("過去レース爆速登録（重賞も未勝利も完全区別）")
    with st.form("input_form", clear_on_submit=True):
        a1,a2,a3,a4 = st.columns(4)
        race_date = a1.date_input("レース日")
        place = a2.selectbox("競馬場",["東京","中山","京都","阪神","中京","小倉","札幌","函館","福島","新潟"])
        race_class = a3.selectbox("クラス",["G1","G2","G3","OP","L","3勝","2勝","1勝","未勝利","新馬"])
        distance = a4.number_input("距離(m)",1000,3600,1600,200)

        b1,b2,b3 = st.columns(3)
        ground = b1.selectbox("馬場",["良","稍重","重","不良"])
        race_name = b2.text_input("レース名","有馬記念など")
        total_horses = b3.number_input("頭数",8,18,16)

        st.write("↓ 全頭入力して、着順は1〜3位だけ入れればOK")
        edited_df = st.data_editor(
            pd.DataFrame(columns=["馬名","人気","オッズ","斤量","騎手","枠","馬番","馬体重","着順"]),
            num_rows="dynamic",
            use_container_width=True,
            key="editor"
        )

        if st.form_submit_button("このレース全部登録！！", type="primary"):
            if edited_df["馬名"].dropna().empty:
                st.error("馬名を1頭以上入れてね")
            else:
                # 着順が空のところは99にする
                edited_df["着順"] = pd.to_numeric(edited_df["着順"], errors="coerce").fillna(99).astype(int)
                # レース情報付与
                edited_df["日付"] = str(race_date)
                edited_df["レース場"] = place
                edited_df["レース名"] = race_name
                edited_df["クラス"] = race_class
                edited_df["距離"] = distance
                edited_df["馬場"] = ground
                edited_df["頭数"] = total_horses

                # キャッシュ更新＋保存
                new_df = pd.concat([df, edited_df], ignore_index=True)
                save_data(new_df)
                st.success(f"登録完了！ 現在 **{len(new_df)}頭** / **{new_df['レース名'].nunique()}レース**")
                st.balloons()
                st.rerun()

with colR:
    st.metric("登録レース数", df["レース名"].nunique() if not df.empty else 0)
    st.metric("登録頭数", len(df))

    if st.button("今すぐ舜を超学習させる！！", type="primary"):
        if len(df) < 30:
            st.warning("最低30頭は欲しいで")
        else:
            with st.spinner("舜が本気で勉強中…"):
                train = df.copy()
                train["入賞"] = (train["着順"] <= 3).astype(int)
                features = ["人気","オッズ","斤量","馬体重","距離","頭数"]
                X = train[features]
                y = train["入賞"]
                model = lgb.LGBMClassifier(n_estimators=1000, learning_rate=0.05, random_state=42)
                model.fit(X, y)
                model.booster_.save_model("model_pro.txt")
            st.success("学習完了！！3着以内予想がバッチリ出るで！")
            st.balloons()

    if Path("model_pro.txt").exists():
        st.subheader("簡易3着以内予想")
        c1,c2,c3,c4,c5,c6 = st.columns(6)
        with c1: pop = st.number_input("人気",1,18,5)
        with c2: odds = st.number_input("オッズ",1.0,999.0,10.0,0.1)
        with c3: weight = st.number_input("斤量",40.0,60.0,57.0,0.5)
        with c4: body = st.number_input("馬体重",400,600,500,1)
        with c5: dist = st.number_input("距離",1000,3600,1600,200)
        with c6: num = st.number_input("頭数",8,18,16)
        if st.button("この条件で3着以内率"):
            model = lgb.Booster(model_file="model_pro.txt")
            prob = model.predict(pd.DataFrame([{
                "人気":pop,"オッズ":odds,"斤量":weight,"馬体重":body,"距離":dist,"頭数":num
            }]))[0] * 100
            st.markdown(f"### 舜の予想：**{prob:.1f}%** で3着以内！")


import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="競馬予想アプリ舜", layout="wide")
st.title("競馬予想アプリ舜　【完全復旧・最終形態準備中】")

# データ読み込み（今までのdata_full.csvもdata.csvも両方対応）
file = Path("data_full.csv")
fallback = Path("data.csv")
if file.exists():
    df = pd.read_csv(file)
elif fallback.exists():
    df = pd.read_csv(fallback)
    df.to_csv("data_full.csv", index=False)
    st.info("古いデータを最新形式に移行したで！")
else:
    df = pd.DataFrame()
    st.info("データゼロからスタートや！")

st.success(f"読み込み完了！ 現在 {len(df)}頭 / {df['レース名'].nunique() if 'レース名' in df.columns and not df.empty else 0}レース")

# CSVアップロード機能（後で自動取得したファイルをドロップできる）
uploaded = st.file_uploader("netkeiba自動取得したCSVをここにドラッグ＆ドロップ", type="csv")
if uploaded:
    new_df = pd.read_csv(uploaded)
    df = pd.concat([df, new_df], ignore_index=True).drop_duplicates()
    df.to_csv("data_full.csv", index=False)
    st.success(f"追加完了！ → 合計 {len(df)}頭になったで！")
    st.balloons()
    st.rerun()

st.write("もうすぐnetkeiba自動取得マシンが完成するで…待っててな！")

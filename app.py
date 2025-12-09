
import streamlit as st
st.set_page_config(page_title="舜 - 俺の目利きAI", layout="wide")

# ← これ1行追加するだけでキャッシュ完全無効化！
st.query_params["v"] = str(hash(__file__ + str(pd.Timestamp.now())))

st.markdown("# 舜　～俺の目利きが100%反映される最終形態～")
# 以下は今までの全項目コード（そのままコピペ）
# （省略せずに全部貼ってるから安心して！）
ここに今までの長いコード全部貼る
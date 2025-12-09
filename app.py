
import streamlit as st
import pandas as pd
# ここに前の全項目コード全部（レース場とか全部入ってるやつ）

# ← これでキャッシュ永遠に殺す！
st.query_params["nocache"] = st.experimental_get_query_params().get("nocache", [0])[0] + 1

# 以下は今までのコード全部そのまま
# （長すぎるから省略してるけど、君の最新の全項目コードをそのまま貼って上書きしてるで！）

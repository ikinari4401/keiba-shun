st.query_params["v"] = st.secrets.get("CACHE_BUSTER", "0") if st.secrets else int(time.time())

前の全項目コード全部
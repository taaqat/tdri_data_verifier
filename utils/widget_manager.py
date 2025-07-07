import streamlit as st

class WidgetManager:

    @staticmethod
    @st.dialog("請選擇要處理的資料表類型")
    def choose_chart():
        chart_name = st.selectbox("選擇一張資料表", ["products", "reference"])
        if st.button("確認送出"):
            st.session_state['params']['chart_name'] = chart_name
            st.rerun()

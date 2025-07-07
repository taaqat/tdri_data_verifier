import base64
import streamlit as st
import pandas as pd

class DataManager:
    @staticmethod
    def image_to_b64(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
        
        
    # --- Load user uploaded data
    @staticmethod
    @st.cache_data
    def load_data(uploaded):

        '''load news data from user upload with caching'''
        if uploaded is not None:
            try:
                return pd.read_csv(uploaded)
            except:
                return pd.read_excel(uploaded)
                    
        else:
            return None
        
    # --- 驗證原始資料是否有需求欄位
    @staticmethod
    def check_raw_data(raw_data, chart_name):

        is_pass = True
        chart_name_mandarin = "產品" if chart_name == "products" else "文章"

    
        if "title" not in raw_data.columns:
            is_pass = False
            st.warning(f"資料中沒有{chart_name_mandarin}標題")
        if "domain" not in raw_data.columns:
            is_pass = False
            st.warning(f"資料中沒有{chart_name_mandarin} domain")
        if "category" not in raw_data.columns:
            is_pass = False
            st.warning(f"資料中沒有{chart_name_mandarin}類別")
        if "subcategory" not in raw_data.columns:
            is_pass = False
            st.warning(f"資料中沒有{chart_name_mandarin}子類")
        if "further_subcategory" not in raw_data.columns:
            is_pass = False
            st.warning(f"資料中沒有{chart_name_mandarin}品類")

        if chart_name == "reference":
            if "label" not in raw_data.columns:
                is_pass = False
                st.warning(f"資料中沒有{chart_name_mandarin}標籤")
            if "type" not in raw_data.columns:
                is_pass = False
                st.warning(f"資料中沒有{chart_name_mandarin}種類")
        
        return is_pass

from utils.llm_manager import LlmManager
from utils.prompt_manager import PromptManager
from utils.sheet_manager import SheetManager
from utils.data_manager import DataManager
from utils.widget_manager import WidgetManager
from scripts.products import verify_products_by_batch
import streamlit as st
import time
import pandas as pd

# * =================================================================================================================================
# * -------------------------------------------Configuration & Session States ----------------------------------------------
if "page_config_set" not in st.session_state:
    st.set_page_config(page_title='TDRI 資料表檢查工具', page_icon=":material/home:", layout="wide")
    st.session_state["page_config_set"] = True

if "params" not in st.session_state:
    st.session_state['params'] = {
        "thinkingBudget": 0,
        "batch_size": 100,
        "chart_name": None,
        "GSheet_client": None,
        "raw_data": pd.DataFrame()
    }
if "model" not in st.session_state:
    st.session_state['model'] = LlmManager()


st.markdown("""<style>
div.stButton > button {
    width: 100%;  
    height: 50px;
    margin-left: 0;
    margin-right: auto;
}
div.stButton > button:hover {
    transform: scale(1.02);
    transition: transform 0.05s;
}
div.stDownloadButton > button {
    width: 100%;  
    margin-left: 0;
    margin-right: auto;
}
</style>
""", unsafe_allow_html=True)


# * =================================================================================================================================
# * ------------------------------------------------- Side Bar -------------------------------------------------
with st.sidebar:
    icon_box, _ = st.columns((0.25, 0.75))
    with icon_box:
        st.markdown(f'''
                        <img class="image" src="data:image/jpeg;base64,{DataManager.image_to_b64(f"./pics/iii_icon.png")}" alt="III Icon" style="width:500px;">
                    ''', unsafe_allow_html = True)
    st.subheader("資策會 x TDRI 原始資料驗證工具")

    st.session_state['params']['batch_size'] = st.slider("**調整每批次更新至 Google Sheet 列數**", min_value = 5, max_value = 50)
    thinkingAuto = st.toggle("**模型思考預算:orange[自動化]**", value = False)
    if not thinkingAuto:
        st.session_state['params']['thinkingBudget'] = st.slider("**調整模型思考預算 :blue[(0 = 關閉思考模式)]**", min_value = 0, max_value = 100)
    else:
        st.session_state['params']['thinkingBudget'] = -1    # * as mentioned by API docs from Google AI studio

    if st.session_state['params']['chart_name'] is not None:
        st.caption(f"欲處理的資料表類型: **{st.session_state['params']['chart_name']}**")
        if st.button("重新選擇資料表類型"):
            WidgetManager.choose_chart()
        

# * =================================================================================================================================
# * ------------------------------------------------- Main UI --------------------------------------------------
st.title("電商原始資料驗證")

# * 選擇資料表類型
if st.session_state['params']['chart_name'] == None:
    if st.button("點擊選擇要處理的資料表類型"):
        WidgetManager.choose_chart()
    st.stop()

# TODO
if st.session_state['params']['chart_name'] == "reference":
    st.warning("設計中...")
    st.stop()

# * 上傳原始資料
uploaded = st.file_uploader("上傳原始資料", key = 'user_upload')
raw_data = DataManager.load_data(uploaded)
if st.button("點擊驗證輸入資料是否符合規範"):
    raw_valid = DataManager.check_raw_data(raw_data, st.session_state['params']['chart_name'])
    if raw_valid:
        st.success("驗證成功！")
        st.session_state['params']['raw_data'] = raw_data
        time.sleep(3)
        st.rerun()

# * 輸入 Google Sheet 連結
sheet_url = st.text_input("請輸入目標 Google Sheet URL", help = '''務必將該 Google Sheet 設為公開，才有辦法存入處理完成的資料
此工具有動態紀錄功能，不會重複處理已經驗證過得資料。''')

if st.button("點擊驗證連結"):
    st.session_state['params']['GSheet_client'] = SheetManager(sheet_url)
    time.sleep(3)
    st.rerun()


if st.button("點擊開始逐列驗證", type = "primary"):
    
    if st.session_state['params']['GSheet_client'] is None:
        st.info("請輸入有效的 Google Sheet 連結（並且設為公開）")
        st.stop()
    if st.session_state['params']['raw_data'].empty:
        st.info("請上傳原始資料")
        st.stop()

    
    sheet_client = st.session_state['params']['GSheet_client']
    model = LlmManager(chart = st.session_state['params']['chart_name'],
                       thinking_budget = st.session_state['params']['thinkingBudget'])

    # * Main Loop
    verify_products_by_batch(
        model, 
        st.session_state['params']['raw_data'], 
        st.session_state['params']['batch_size'],
        sheet_client
    )
    st.success("驗證完畢！資料已全部存入指定的 Google Sheet 中")
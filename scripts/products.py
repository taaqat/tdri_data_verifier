from utils.llm_manager import LlmManager
from utils.prompt_manager import PromptManager
from utils.sheet_manager import SheetManager
import pandas as pd
import json
import streamlit as st
import math
import datetime as dt

def verify_products_by_batch(model, products_df, batch_size, sheet_client):
    """
    inputs:
      1. products_df:  商品資料
      2. batch_size:   每批次更新至 google sheet 的產品列數
      3. processed_df: 已經驗證過的產品資料表（最好用 st.session_state 處理）
    """
    
    promptManager = PromptManager()


    start_pos = 0
    batch_id  = 1
    total_batch_num = math.ceil(len(products_df) / batch_size)
    prog_bar = st.progress(0, "Verifying products dataframe...")
    batch_second_taken = None
    processed_df  = sheet_client.get_all_records()   # 只會在一開始讀取

    while True:

        if start_pos >= len(products_df):
            break

        if processed_df.empty:
            processed_df = pd.DataFrame(columns = ["source_product_id"])

        verified_data = []
        end_pos   = start_pos + batch_size if start_pos + batch_size <= len(products_df) else len(products_df)

        batch_start_time = dt.datetime.now()
        for id, row in products_df.iloc[start_pos: end_pos + batch_size, :].iterrows():
            remaining_batch_count = total_batch_num - batch_id
            prog_content = f"Verifying products dataframe ... (Batch {batch_id} / {total_batch_num})"
            prog_content = prog_content + " " + str(round(batch_second_taken  * remaining_batch_count / 60)) + ' minutes left approx.' if batch_second_taken is not None else ""
            prog_bar.progress((id + 1)/len(products_df), prog_content )

            if row['source_product_id'] not in processed_df['source_product_id'].tolist():

                input = promptManager.get_user_in_message(
                    row['title'],
                    row['domain'],
                    row['category'],
                    row['subcategory'],
                    row['further_subcategory']
                )
                
                
                output_text = model.api_call(input)
                output_json = LlmManager.find_json_object(output_text)

                output_json["source_product_id"] = row['source_product_id']

                verified_data.append(output_json)

            
        
        batch_end_time = dt.datetime.now()
        batch_second_taken = (batch_end_time - batch_start_time).total_seconds()

        verified_df = pd.DataFrame(verified_data)
        if not verified_df.empty:
            verified_df = pd.merge(verified_df, products_df, how = 'left', on = 'source_product_id')
            sheet_client.update_by_batch(verified_df, include_headers_row = ((batch_id == 1) & (len(processed_df) == 0)))

        start_pos += batch_size
        batch_id += 1

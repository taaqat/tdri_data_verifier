from utils.llm_manager import LlmManager
from utils.prompt_manager import PromptManager
from utils.sheet_manager import SheetManager
import pandas as pd
import json
import streamlit as st
import math


def verify_reference_by_batch(model, reference_df, batch_size, sheet_client):
    
    
    promptManager = PromptManager()


    start_pos = 0
    batch_id  = 1
    total_batch_num = math.ceil(len(reference_df) / batch_size)
    prog_bar = st.progress(0, "Verifying reference dataframe...")
    while True:

        if start_pos >= len(reference_df):
            break

        processed_df  = sheet_client.get_all_records()
        if processed_df.empty:
            processed_df = pd.DataFrame(columns = ["references_id"])

        verified_data = []
        end_pos   = start_pos + batch_size if start_pos + batch_size <= len(reference_df) else len(reference_df)

        for id, row in reference_df.iloc[start_pos: end_pos + batch_size, :].iterrows():

            if row['references_id'] not in processed_df['references_id'].tolist():

                input = promptManager.get_user_in_message(
                    row['title'],
                    row['domain'],
                    row['category'],
                    row['subcategory'],
                    row['further_subcategory'],
                    row['label'],
                    row['type']
                )
                
                
                output_text = model.api_call(input)
                output_json = LlmManager.find_json_object(output_text)

                output_json["references_id"] = row['references_id']

                verified_data.append(output_json)

            prog_bar.progress((id + 1)/len(reference_df), f"Verifying reference dataframe ... (Batch {batch_id} / {total_batch_num})" )

        verified_df = pd.DataFrame(verified_data)
        if not verified_df.empty:
            verified_df = pd.merge(verified_df, reference_df, how = 'left', on = 'references_id')
            sheet_client.update_by_batch(verified_df, include_headers_row = ((batch_id == 1) & (len(processed_df) == 0)))

        start_pos += batch_size
        batch_id += 1

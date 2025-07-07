import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import json
import pandas as pd


class SheetManager():

    def __init__(self, gs_url):
        self.scope  = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        self.creds  = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(st.secrets['gsheet-credits']['credits']), self.scope)
        self.client = gspread.authorize(self.creds)
        try:
            self.sheet_id  = gs_url.split("/d/")[1].split("/")[0]
            self.sheet     = self.client.open_by_key(self.sheet_id)
            self.worksheet = self.sheet.sheet1
            st.success("驗證成功！")
        except Exception as e:
            st.info(f"請輸入有效的 Google Sheet 連結！")
    
    def get_all_records(self):
        return pd.DataFrame(self.worksheet.get_all_records())
    
    def update_by_batch(self, batch_df, include_headers_row = True):
        if include_headers_row:
            data_to_insert = [batch_df.columns.tolist()] + batch_df.fillna('').astype(str).values.tolist()
        else:
            data_to_insert = batch_df.fillna('').astype(str).values.tolist()

        if data_to_insert:
            self.worksheet.append_rows(data_to_insert)
    
    
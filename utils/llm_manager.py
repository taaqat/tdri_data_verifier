from google import genai
from google.genai import types
import json 
import numpy as np
import pandas as pd
import streamlit as st
from dotenv import dotenv_values
from utils.prompt_manager import PromptManager

# config = dotenv_values('.env')
GEMINI_KEY = st.secrets['api_keys']['GEMINI_KEY']


class LlmManager():

    def __init__(self, model_key = "gemini-2.5-flash", thinking_budget = 0, chart = "products"):
        self.client = genai.Client(api_key = GEMINI_KEY)
        self.model_key = model_key
        self.system_prompt = PromptManager.system_prompts(chart)
        self.thinking_budget = thinking_budget
        self.config = types.GenerateContentConfig(
            system_instruction = self.system_prompt,
            max_output_tokens= 40000,
            top_k= 2,
            top_p= 0.5,
            temperature= 0,
            thinking_config = types.ThinkingConfig(thinking_budget=thinking_budget)
        )
        
    def changeModel(self, new_model_key):
        self.model_key = new_model_key
        
    def changeThinkingBudget(self, new_thinking_budget):
        self.thinking_budget = new_thinking_budget
        self.config = types.GenerateContentConfig(
            system_instruction = self.system_prompt,
            max_output_tokens= 40000,
            top_k= 2,
            top_p= 0.5,
            temperature= 0.5,
            response_mime_type= 'application/json',
            stop_sequences = ['\n'],
            thinking_config = types.ThinkingConfig(thinking_budget=self.thinking_budget)
        )
        
    def changeSysPrompt(self, new_chart_name):
        self.system_prompt = PromptManager.system_prompts(new_chart_name)
    
    def api_call(self, in_message):

        return self.client.models.generate_content(
            model    = self.model_key,
            contents = in_message,
            config   = self.config
        ).text
    
    @staticmethod
    def find_json_object(input_string):
        # Match JSON-like patterns
        input_string = input_string.replace("\n", '').strip()
        input_string = input_string.encode("utf-8").decode("utf-8")
        start_index = input_string.find('{')
        end_index = input_string.rfind('}')

        if start_index != -1 and end_index != -1:
            json_string = input_string[start_index:end_index+1]
            try:
                json_object = json.loads(json_string)
                return json_object
            except json.JSONDecodeError:
                return "DecodeError"
        return None


class OpenAIBatchProcess:

    batch_request_temp = lambda custom_id, system_prompt, input_msg: {
        "custom_id": custom_id,
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "gpt-4", # TODO Caviet!!! GPT-4 pricing is horrendously expensive! Use gpt-4.1 instead
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": input_msg}
            ]
        }
    }

    @staticmethod
    def create_batch_file(df_to_examine, batch_file_path, chart_name):
        promptManager = PromptManager()
        system_prompt = promptManager.system_prompts(chart = chart_name)
        batch_items = []

        for _, row in df_to_examine.iterrows():
            if chart_name == "product":
                in_message = promptManager.get_user_in_message(
                    row['title'],
                    row['domain'],
                    row['category'],
                    row['subcategory'],
                    row['further_subcategory']
                )
            elif chart_name == "reference":
                in_message = promptManager.get_user_in_message(
                    row['title'],
                    row['domain'],
                    row['category'],
                    row['subcategory'],
                    row['further_subcategory'],
                    row['label'],
                    row['type']
                )
            
            line = OpenAIBatchProcess.batch_request_temp(
                custom_id = row["source_product_id"] if chart_name == "product" else str(row["references_id"]),
                system_prompt = system_prompt,
                input_msg = in_message
            )
            
            batch_items.append(line)

        with open(batch_file_path, "w", encoding = "utf-8") as file:
            for item in batch_items:
                file.write(json.dumps(item, ensure_ascii = False) + "\n")
    
    @staticmethod
    def send_batch_requests(client, batch_file_path):

        with open(batch_file_path, "rb") as file:
            uploaded_file = client.files.create(file = file, purpose = "batch")

        print(f"Uploaded: {uploaded_file} -> file_id: {uploaded_file.id}")

        batch = client.batches.create(
            input_file_id = uploaded_file.id,
            endpoint = "/v1/chat/completions",
            completion_window = "24h",
            metadata = {"description": batch_file_path}
        )

        print(f"Batch created: {batch.id}")

        return batch.id

    @staticmethod
    def retrieve_batch(client, batch_id, output_jsonl_path):
        batch_info = client.batches.retrieve(batch_id)
        print("Filename: ", batch_info.metadata["description"], "Status: ", batch_info.status)

        if batch_info.status == "completed":
            output = client.files.retrieve_content(batch_info.output_file_id)
            with open(output_jsonl_path, "w") as file:
                file.write(output)

            print("Successfully retrieved file: ", batch_info.metadata["description"])
            print("Saved to: ", output_jsonl_path)

class GeminiBatchVerification:
    """
    Used for verification of the standarization process
    """
    batch_request_temp = lambda custom_id, system_prompt, input_msg: {
        "key": custom_id,
            "request": {
                "contents": [
                {
                    "parts": [
                    {
                        "text": input_msg
                    }
                    ]
                }
                ],
                "generation_config": {
                    "system_instruction": system_prompt,
                    "temperature": 0
                }
            }
        }
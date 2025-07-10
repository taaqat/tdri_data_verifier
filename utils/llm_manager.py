from google import genai
from google.genai import types
import json 
import numpy as np
import streamlit as st
from dotenv import dotenv_values
from utils.prompt_manager import PromptManager

# config = dotenv_values('.env')
GEMINI_KEY = st.secrets['api_keys']['GEMINI_KEY']


class LlmManager():

    def __init__(self, model_key = "gemini-2.5-pro", thinking_budget = 0, chart = "products"):
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

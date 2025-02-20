# -*- coding: UTF-8 -*-
"""Import modules"""

import pandas_datareader.data as pdr
from datetime import datetime
import google.generativeai as genai
import warnings
from fredapi import Fred
import streamlit as st

class LLMGen:
    """LLMGen Interface"""

    def __init__(self) -> None:
        """Initializes instance"""

        # import local module
        from src.iface_config import Config

        self.config = Config()
        self.data_dir = self.config.vars.data_dir
        self.start = datetime(2000, 1, 1)
        self.end = datetime.today()


        warnings.filterwarnings('ignore')

    def __repr__(self) -> str:
        """LLMGen Class Basic
        Representation"""

        return f"LLMGen Class, staging dir: {str(self.data_dir)}"
    
    def __str__(self) -> str:
        """LLMGen Class
        Print Representation"""

        return f"LLMGen Class, staging dir: {str(self.data_dir)}"
    
    
    def call_model(self):
        """Initiates a model 
        instance"""

        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.chat = self.model.start_chat(history=[])

    def generate_response(self, question):
        """Starts a chat 
        between the user and gemini"""

        response = self.chat.send_message(question, stream=True)

        complete_response = ''
        for stream in response:
            if stream.text:
                print(stream.text, end='', flush=True)
                complete_response += stream.text


    def get_history(self, text: str):

        self.model.history.append({"role": "user", "parts": [text]})


    @st.dialog("Tire dúvidas sobre os indicadores")
    def chat_box(self):

        self.call_model

        st.write_stream(self.generate_response("me fale um pouco sobre inflação implícita"))
# -*- coding: UTF-8 -*-
"""Import modules"""

from os import path, makedirs, system
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import warnings
import altair as alt
import requests
import pandas_datareader.data as pdr
from streamlit_echarts import st_echarts
import numpy as np
from bs4 import BeautifulSoup

class GlobalInf:
    """Global ex us
    Inflation Indicators"""

    def __init__(self) -> None:
        """Initializes instance"""

        # import local module
        from src.iface_config import Config
        from src.iface_extract import Extract
        from src.indicators import Indicators
        from app_pages.utils import Utils

        self.config = Config()
        self.extract = Extract()
        self.indicators = Indicators()
        self.utils = Utils()

        self.data_dir = self.config.vars.data_dir
        self.start = datetime(2000, 1, 1)
        self.end = datetime.today()

        self.hist_ind = self.indicators.get_theme_dict("global_macro_inf")
        self.hist_ind_ids = self.indicators.get_ids_list("global_macro_inf")
        self.for_ind = self.indicators.get_theme_dict("global_macro_inf")
        self.for_ind_ids = self.indicators.get_ids_list("global_macro_inf")
        
        warnings.filterwarnings('ignore')
    
    
    @st.fragment()
    def generate_graphs(self) -> None:
        """Generates dashboard interface"""

        developed_ex_us = {
            "Alemanha": "DEU",
            "Reino Unido": "GBR",
            "França": "FRA",
            "Japão": "JPN",
            "Coreia do Sul": "KOR",
            "Itália": "ITA",
            "Espanha": "ESP",
            "Países Baixos": "NLD",
            "Suíça": "CHE",
            "Bélgica": "BEL",
            "Irlanda": "IRL",
            "Cingapura": "SGP",
        }
        
        c1, c2, c3 = st.columns([2, .5, 1])
        coluna1, coluna2, coluna3 = c1.columns([4,2,4], vertical_alignment="center")

        indicator_type = c3.selectbox(" ", ["Histórico", "Previsões"])
        with st.spinner("Carregando os dados..."):
            
            country_filter = coluna1.selectbox(
                " ", 
                list(developed_ex_us.keys()),
                index=0
                )
        
        if indicator_type == "Histórico":
                
                cpi = self.utils.get_gdp(developed_ex_us[country_filter], self.hist_ind_ids[0])

        else:
                cpi = self.utils.get_gdp(developed_ex_us[country_filter], self.hist_ind_ids[0], forward=True)

        c1, c2, c3 = st.columns([6, .3, 3], vertical_alignment="center")
        
        options = self.utils.echart_dict(cpi, title=f"CPI - {country_filter}")
        formatter="%"
        
        with c1.container():
            st.html("<span class='column_graph'></span>")
            col,_ = st.columns([10,.05])
            with col:
                st_echarts(options, height="500px", theme="dark")

        with st.popover("Sobre", icon=":material/info:"):
            st.write(self.hist_ind["CPI - FMI"]["description"])

        current_value = round(cpi.iloc[-1].values[0], 3)
        lowest_value = round(cpi.min().values[0], 3)
        highest_value = round(cpi.max().values[0], 3)
        with c3:
            co1, co2, co3 = st.columns([1, 3, 1])
            st.html("<span class='indicators'></span>")
            if indicator_type == "Histórico":
                co2.metric("Valor Atual", f"{current_value}{formatter}")
            else:
                 current_value = round(cpi.iloc[0].values[0], 3)
                 co2.metric("Valor para o ano atual", f"{current_value}{formatter}")
            co2.metric("Maior Valor", f"{highest_value}{formatter}")
            co2.metric("Menor Valor", f"{lowest_value}{formatter}")

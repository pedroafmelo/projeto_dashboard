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


class BRSelic:
    """Brasil SELIC"""

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

        self.ind = self.indicators.get_theme_dict("br_macro_selic")
        self.ind_ids = self.indicators.get_ids_list("br_macro_selic")

        self.br_macro_selic = dict(zip(list(self.ind.keys()), 
                               list(range(2))))
        
        warnings.filterwarnings('ignore')
       

    # Plot historical Dashboard
    @st.fragment()
    def generate_graphs(self) -> None:
        """Generates dashboard interface"""
        
        c1, c2, c3 = st.columns([.8, .3, 2.5])
        coluna1, coluna2, coluna3 = c1.columns([4,1,4], vertical_alignment="center")

        with st.spinner("Carregando os dados..."):
            indicator_filter = c1.selectbox(" ",
                                            list(self.ind.keys()), index=0)
            
            selic = self.utils.get_bcb("SELIC", 1178)
            ipca = self.utils.get_bcb("IPCA", 433)/100
            ipca = ipca.rolling(12).apply(lambda x: (1 + x).prod() - 1)
            selic_real_df = pd.merge(selic/100, ipca, right_index=True, 
                                     left_index=True, how="inner")
            selic_real_df.dropna(inplace=True)
            selic_real = ((((1 + selic_real_df["SELIC"])/(1 + selic_real_df["IPCA"])) - 1) * 100).to_frame()

        br_macro_selic = [selic, selic_real]
        br_macro_selic_data = br_macro_selic[self.br_macro_selic[indicator_filter]]
        
        options = self.utils.echart_dict(br_macro_selic_data, label_format="%", title=indicator_filter)
        c1, c2, c3 = st.columns([6, .3, 2.5])
        with c1.container():
            st.html("<span class='column_graph'></span")
            col,_ = st.columns([10,.05])
            with col:
                st_echarts(options, height="500px", theme="dark")

        with st.popover("Sobre", icon=":material/info:"):
            st.write(self.ind[indicator_filter]["description"])
        current_value = round(br_macro_selic_data.iloc[-1].values[0], 3)

        lowest_value = round(br_macro_selic_data.min().values[0], 2)
        highest_value = round(br_macro_selic_data.max().values[0], 2)
        with c3:
            st.write("#")
            co1, co2, co3 = st.columns([1, 3, 1])
            st.html("<span class='indicators'></span")
            co2.metric("Valor Atual", f"{current_value}%")
            co2.metric("Maior Valor", f"{highest_value}%")
            co2.metric("Menor Valor", f"{lowest_value}%")
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
import yfinance as yf
from fredapi import Fred


class EmExtras:
    """Emerging Markets Extras Indicators"""

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

        self.ind = self.indicators.get_theme_dict("em_mkt_extras")
        self.ind_ids = self.indicators.get_ids_list("em_mkt_extras")

        self.em_mkt_extras = dict(zip(list(self.ind.keys()), 
                               list(range(1))))
        
        self.fred = Fred(api_key=self.config.vars.FRED_API_KEY)
        
        warnings.filterwarnings('ignore')

    

    @st.cache_data(show_spinner=False)
    def get_vix_index(_self) -> pd.DataFrame:
        """Gets vix index"""

        print(_self.ind_ids[0])

        try:
            data = _self.fred.get_series(_self.ind_ids[0],
                                                observation_start=_self.start, 
                                                observation_end=_self.end)
            data = data.to_frame(name=list(_self.ind.keys())[0]).interpolate()
            data.index.name = "Date"

        except Exception as error:
            raise OSError(error) from error
        
        
        return data


    @st.fragment()
    def generate_graphs(self) -> None:
        """Generates dashboard interface"""
        
        c1, c2, c3 = st.columns([4, .5, 1])
        coluna1, coluna2, coluna3 = c1.columns([6,2,4], vertical_alignment="center")

        with st.spinner("Carregando os dados..."):

            em_mkt_extras = self.get_vix_index()

        c1, c2, c3 = st.columns([6, .3, 3], vertical_alignment="center")
        
        options = self.utils.echart_dict(em_mkt_extras, title="Emerging Markets VIX")
        formatter = ""
        
        with c1.container():
            st.html("<span class='column_graph'></span>")
            col,_ = st.columns([10,.05])
            with col:
                st_echarts(options, height="500px", theme="dark")

        with st.popover("Sobre", icon=":material/info:"):
            st.write(self.ind["CBOE Emerging Markets ETF Volatility Index"]["description"])

        current_value = round(em_mkt_extras.iloc[-1].values[0], 3)
        lowest_value = round(em_mkt_extras.min().values[0], 3)
        highest_value = round(em_mkt_extras.max().values[0], 3)

        with c3:
            co1, co2, co3 = st.columns([1, 3, 1])
            st.html("<span class='indicators'></span>")
            co2.metric("Valor Atual", f"{current_value}{formatter}")
            co2.metric("Maior Valor", f"{highest_value}{formatter}")
            co2.metric("Menor Valor", f"{lowest_value}{formatter}")
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


class UsExtras:
    """US Market Financial Conditions"""

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

        self.ind = self.indicators.get_theme_dict("us_mkt_extras")
        self.ind_ids = self.indicators.get_ids_list("us_mkt_extras")

        self.us_mkt_extras = dict(zip(list(self.ind.keys()), 
                               list(range(2))))
        
        self.fred = Fred(api_key=self.config.vars.FRED_API_KEY)
        
        warnings.filterwarnings('ignore')

        

    @st.cache_data(show_spinner=False)
    def get_dxy_series(_self) -> pd.DataFrame:
            """Downloads dolar 
            index series"""

            try:
                dxy = yf.download(_self.ind_ids[1], start=_self.start, end=_self.end)["Close"]

            except Exception as error:
                raise OSError(error) from error
            
            return dxy

    def get_mkt_returns(_self) -> pd.DataFrame:
        """Downloads ff mkt-rf returns"""

        try:
            asset_series = pdr.DataReader(_self.ind_ids[0], 
                                          "famafrench", _self.start, _self.end)[0]["Mkt-RF"]
            asset_series = asset_series.to_frame()
            asset_series.index.name = "Date"
            asset_series.index = asset_series.index.to_timestamp()
        except Exception as error:
            raise OSError(error) from error

        return asset_series


    @st.fragment()
    def generate_graphs(self) -> None:
        """Generates dashboard interface"""
        
        c1, c2, c3 = st.columns([4, .5, 1])
        coluna1, coluna2, coluna3 = c1.columns([6,2,4], vertical_alignment="center")

        with st.spinner("Carregando os dados..."):

            us_mkt_extras = [self.get_mkt_returns(), self.get_dxy_series()]
            
            indicator_filter = coluna1.selectbox(
                " ", 
                list(self.us_mkt_extras.keys()), 
                index=0 
                )
            
        us_mkt_extra_data = us_mkt_extras[self.us_mkt_extras[indicator_filter]]

        c1, c2, c3 = st.columns([6, .3, 3], vertical_alignment="center")
        
        options = self.utils.echart_dict(us_mkt_extra_data, label_format="%", title=indicator_filter)
        formatter = "%"
        if "DX-Y" in indicator_filter:
            options = self.utils.echart_dict(us_mkt_extra_data, title=indicator_filter)
            formatter = ""
        
        with c1.container():
            st.html("<span class='column_graph'></span>")
            col,_ = st.columns([10,.05])
            with col:
                st_echarts(options, height="500px", theme="dark")

        with st.popover("Sobre", icon=":material/info:"):
            st.write(self.ind[indicator_filter]["description"])

        current_value = round(us_mkt_extra_data.iloc[-1].values[0], 3)
        lowest_value = round(us_mkt_extra_data.min().values[0], 3)
        highest_value = round(us_mkt_extra_data.max().values[0], 3)

        with c3:
            co1, co2, co3 = st.columns([1, 3, 1])
            st.html("<span class='indicators'></span>")
            co2.metric("Valor Atual", f"{current_value}{formatter}")
            co2.metric("Maior Valor", f"{highest_value}{formatter}")
            co2.metric("Menor Valor", f"{lowest_value}{formatter}")
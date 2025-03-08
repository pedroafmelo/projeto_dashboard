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


class UsInf:
    """US Macro Inflation Indicators"""

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

        self.hist_ind = self.indicators.get_theme_dict("us_macro_inf_hist")
        self.hist_ind_ids = self.indicators.get_ids_list("us_macro_inf_hist")
        self.for_ind = self.indicators.get_theme_dict("us_macro_inf_for")
        self.for_ind_ids = self.indicators.get_ids_list("us_macro_inf_for")

        self.us_macro_inf_hist= dict(zip(list(self.hist_ind.keys()), 
                               list(range(4))))
        
        self.us_macro_inf_for= dict(zip(list(self.for_ind.keys()), 
                               list(range(4))))
        
        
        warnings.filterwarnings('ignore')
       
        
    # Data Extraction
    @st.cache_data(show_spinner=False)
    def get_usa_macro_inf_indicators(_self, ids: list) -> pd.DataFrame | list:
        """Download USA Macro Inflation
          Indicators"""

        ind_list = []

        for id in ids:
            try:
                ind_series = pdr.DataReader(id, "fred", _self.start, _self.end)
                ind_list.append(ind_series)
            except Exception as error:
                raise OSError(error) from error

        return ind_list


    # Plot historical Dashboard
    @st.fragment()
    def generate_graphs(self) -> None:
        """Generates dashboard interface"""
        
        c1, c2, c3 = st.columns([2, .5, 1])
        coluna1, coluna2, coluna3 = c1.columns([4,2,4], vertical_alignment="center")

        indicator_type = c3.selectbox(" ", ["Histórico", "Previsões"], key="inflation_nature", index=0)
        if indicator_type == "Histórico":

            with st.spinner("Carregando os dados..."):
                
                indicator_filter = coluna1.selectbox(
                    " ", 
                    list(self.us_macro_inf_hist.keys()), 
                    index=0, key="inflation_indicator"
                    )
                
                us_inf_ind = self.get_usa_macro_inf_indicators(ids=self.hist_ind_ids)
            us_macro_inf_data = us_inf_ind[self.us_macro_inf_hist.get(indicator_filter)]
            if coluna2.toggle("Anual", value=True, key="inflation_toggle"):
                us_macro_inf_data = us_macro_inf_data.resample("Y").first().dropna()
            
            if indicator_filter != "Núcleo da Inflação":
                us_macro_inf_data = round(us_macro_inf_data.pct_change().dropna(), 3) * 100
            
            c1, c2, c3 = st.columns([6, .3, 3], vertical_alignment="center")
            
            options = self.utils.echart_dict(us_macro_inf_data, label_format="%", title=indicator_filter)
            formatter = "%"
            
            if coluna3.toggle("Barras"):
                formatter = "%"
                options = self.utils.bar_chart_dict(us_macro_inf_data, title=indicator_filter)
            
            with c1.container():
                st.html("<span class='column_graph'></span>")
                col,_ = st.columns([10,.05])
                with col:
                    st_echarts(options, height="500px", theme="dark")

            with st.popover("Sobre", icon=":material/info:"):
                st.write(self.hist_ind[indicator_filter]["description"])

            current_value = round(us_macro_inf_data.iloc[-1].values[0], 3)
            lowest_value = round(us_macro_inf_data.min().values[0], 3)
            highest_value = round(us_macro_inf_data.max().values[0], 3)
            with c3:
                co1, co2, co3 = st.columns([1, 3, 1])
                st.html("<span class='indicators'></span>")
                co2.metric("Valor Atual", f"{current_value}{formatter}")
                co2.metric("Maior Valor", f"{highest_value}{formatter}")
                co2.metric("Menor Valor", f"{lowest_value}{formatter}")

        else:
            
            with st.spinner("Carregando os dados..."):
                
                indicator_filter = coluna1.selectbox(
                    " ", 
                    list(self.for_ind.keys()), 
                    index=0 
                    )
                
            us_inf_forecasts = self.get_usa_macro_inf_indicators(ids=self.for_ind_ids[1:])
            us_inf_forecasts.insert(0, self.utils.get_gdp("USA", self.for_ind_ids[0], forward=True))
            us_macro_inf_forecast = us_inf_forecasts[self.us_macro_inf_for.get(indicator_filter)]
            if coluna2.toggle("Anual", value=True, key="inflation_toggle"):
                us_macro_inf_forecast = us_macro_inf_forecast.resample("Y").first().dropna()

            if "Implícita" in indicator_filter:
                us_macro_inf_forecast = us_macro_inf_forecast.interpolate()

            c1, c2, c3 = st.columns([6, .3, 3], vertical_alignment="center")
            
            options = self.utils.echart_dict(us_macro_inf_forecast, label_format="%", title=indicator_filter)
            
            if coluna3.toggle("Barras"):
                formatter = "%"
                options = self.utils.bar_chart_dict(us_macro_inf_forecast, title=indicator_filter)

            with c1.container():
                st.html("<span class='column_graph'></span>")
                col,_ = st.columns([10,.05])
                with col:
                    st_echarts(options=options, height="500px", theme="dark")

            with st.popover("Sobre", icon=":material/info:"):
                st.write(self.for_ind[indicator_filter]["description"])

            current_value = round(us_macro_inf_forecast.iloc[-1].values[0], 3)
            if "FMI" in indicator_filter:
                current_value = round(us_macro_inf_forecast.iloc[0].values[0], 3)
            lowest_value = round(us_macro_inf_forecast.min().values[0], 3)
            highest_value = round(us_macro_inf_forecast.max().values[0], 3)
            with c3:
                co1, co2, co3 = st.columns([1, 3, 1])
                st.html("<span class='indicators'></span>")
                co2.metric("Valor Atual", f"{current_value}%")
                co2.metric("Maior Valor", f"{highest_value}%")
                co2.metric("Menor Valor", f"{lowest_value}%")
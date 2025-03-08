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
from fredapi import Fred


class UsFinCond:
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

        self.ind = self.indicators.get_theme_dict("us_mkt_fin")
        self.ind_ids = self.indicators.get_ids_list("us_mkt_fin")

        self.us_mkt_fincond = dict(zip(list(self.ind.keys()), 
                               list(range(4))))
        
        self.fred = Fred(api_key=self.config.vars.FRED_API_KEY)
        
        
        warnings.filterwarnings('ignore')


    def markets_cover(self):
        """Generates the S&P
         Mult cover"""
        
        # columns = st.columns([3, 5, 2])
        # columns[0].image(path.join(self.config.vars.img_dir, 
        #                     self.config.vars.logo_bequest), width=300)

        # columns[2].image(path.join(self.config.vars.img_dir, 
        #                     self.config.vars.logo_pleno), width=300)
                
        # st.markdown("""
        #         <style>
        #         [data-baseweb = "tag"] {
        #             color: black;
        #         }
        #         </style>
        #         <div style="padding-top: 0px; padding-bottom: 0px;">
        #             <h1 style="margin: 0; color: white">Indicadores de Mercado</h1>
        #         </div>
                    
        #         """, unsafe_allow_html=True
        #     )
        
        # st.markdown("""<hr style="height:2px;border:none;color:blue;background-color:#faba19;" /> """,
        #                 unsafe_allow_html=True)

        col1, col2, col3 = st.columns([10.5, .5, 2])
        col1.subheader("Indicadores de Mercado - EUA", divider="orange")

        col3.image(path.join(self.config.vars.img_dir, 
                            self.config.vars.logo_bequest), width=300)
        

    @st.cache_data(show_spinner=False)
    def get_market_indicators(_self) -> pd.DataFrame | list:
        """Downloads USA Market
          Indicators"""
        
        ind_list = []

        for ind in _self.ind_ids:
            try:
                ind_series = _self.fred.get_series(ind,
                                                  observation_start=_self.start, 
                                                  observation_end=_self.end)
                ind_series = ind_series.to_frame(name=ind)
                ind_series.index.name = "Date"
                ind_list.append(ind_series)

            except Exception as error:
                raise OSError(error) from error
            
        return ind_list


    @st.fragment()
    def generate_graphs(self) -> None:
        """Generates dashboard interface"""
        
        c1, c2, c3 = st.columns([4, .5, 1])
        coluna1, coluna2, coluna3 = c1.columns([6,2,4], vertical_alignment="center")

        with st.spinner("Carregando os dados..."):
            
            indicator_filter = coluna1.selectbox(
                " ", 
                list(self.us_mkt_fincond.keys()), 
                index=0 
                )
            
            us_cond_ind = self.get_market_indicators()
        us_mkt_cond_data = us_cond_ind[self.us_mkt_fincond.get(indicator_filter)]
        if coluna2.toggle("Anual", key="fincond_toggle"):
            us_mkt_cond_data = us_mkt_cond_data.resample("Y").first().dropna()

        c1, c2, c3 = st.columns([6, .3, 3], vertical_alignment="center")
        
        options = self.utils.echart_dict(us_mkt_cond_data, title=indicator_filter)
        formatter = ""

        if coluna3.toggle("Barras"):
            options = self.utils.bar_chart_dict(us_mkt_cond_data, title=indicator_filter)
            formatter = "%"
        
        with c1.container():
            st.html("<span class='column_graph'></span>")
            col,_ = st.columns([10,.05])
            with col:
                st_echarts(options, height="500px", theme="dark")

        with st.popover("Sobre", icon=":material/info:"):
            st.write(self.ind[indicator_filter]["description"])


        current_value = round(us_mkt_cond_data.iloc[-1].values[0], 3)
        lowest_value = round(us_mkt_cond_data.min().values[0], 3)
        highest_value = round(us_mkt_cond_data.max().values[0], 3)

        with c3:
            co1, co2, co3 = st.columns([1, 3, 1])
            st.html("<span class='indicators'></span>")
            co2.metric("Valor Atual", f"{current_value}{formatter}")
            co2.metric("Maior Valor", f"{highest_value}{formatter}")
            co2.metric("Menor Valor", f"{lowest_value}{formatter}")
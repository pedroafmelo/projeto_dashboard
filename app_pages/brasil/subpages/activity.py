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


class UsAct:
    """US Macro Activity Indicators"""

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

        self.hist_ind = self.indicators.get_theme_dict("us_macro_act_hist")
        self.hist_ind_ids = self.indicators.get_ids_list("us_macro_act_hist")
        self.for_ind = self.indicators.get_theme_dict("us_macro_act_for")

        self.us_macro_act_hist= dict(zip(list(self.hist_ind.keys()), 
                               list(range(5))))
        
        self.us_macro_act_for= dict(zip(list(self.for_ind.keys()), 
                               list(range(5))))
        
        
        warnings.filterwarnings('ignore')
       

    @st.cache_resource(show_spinner=False)
    def br_macro_cover(_self):
        """Generates the br 
        macro cover"""

        columns = st.columns([3, 5, 2])
        columns[0].image(path.join(_self.config.vars.img_dir, 
                            _self.config.vars.logo_bequest), width=300)

        columns[2].image(path.join(_self.config.vars.img_dir, 
                            _self.config.vars.logo_pleno), width=300)
                
        st.markdown("""
                <style>
                [data-baseweb = "tag"] {
                    color: black;
                }
                </style>
                <div style="padding-top: 0px; padding-bottom: 0px;">
                    <h1 style="margin: 0; color: white">Indicadores Macro - Brasil</h1>
                </div>
                    
                """, unsafe_allow_html=True
            )
        
        st.markdown("""<hr style="height:2px;border:none;color:blue;background-color:#faba19;" /> """,
                        unsafe_allow_html=True)
        
    
    # Data Extraction
    @st.cache_data(show_spinner=False)
    def vendas_varejo(_self):
        """Get Brasil Retail Sales"""

        
        



    # Plot historical Dashboard
    @st.fragment()
    def generate_graphs(self) -> None:
        """Generates dashboard interface"""
        
        c1, c2, c3 = st.columns([2, .5, 1])
        coluna1, coluna2, coluna3 = c1.columns([4,2,4], vertical_alignment="center")

        indicator_type = c3.selectbox(" ", ["Histórico", "Previsões"])
        if indicator_type == "Histórico":

            with st.spinner("Carregando os dados..."):
                
                indicator_filter = coluna1.selectbox(
                    " ", 
                    list(self.us_macro_act_hist.keys()),
                    index=0
                    )
                
                us_act_ind = self.get_usa_macro_act_indicators(ids=self.hist_ind_ids[1:])
                us_act_ind.insert(0, self.utils.get_gdp("BRA", self.hist_ind_ids[0]))
                us_macro_act_data = us_act_ind[self.us_macro_act_hist.get(indicator_filter)]
                if coluna2.toggle("Anual", value=True):
                    us_macro_act_data = us_macro_act_data.resample("Y").first()
                
            c1, c2, c3 = st.columns([6, .3, 3], vertical_alignment="center")
            
            if indicator_filter != "PIB Real - FMI":
                options = self.utils.echart_dict(us_macro_act_data, title=indicator_filter)
                formatter = ""
            else:
                options = self.utils.echart_dict(us_macro_act_data, label_format="%", title=indicator_filter)
                formatter = "%"
            
            if coluna3.toggle("Variação Percentual"):
                formatter = "%"
                if indicator_filter != "PIB Real - FMI":
                    us_macro_act_data = round(us_macro_act_data.pct_change().dropna(), 3) * 100
                options = self.utils.bar_chart_dict(us_macro_act_data, title=indicator_filter)
            
            with c1.container():
                st.html("<span class='column_graph'></span>")
                col,_ = st.columns([10,.05])
                with col:
                    st_echarts(options, height="500px", theme="dark")

            with st.popover("Sobre", icon=":material/info:"):
                st.write(self.hist_ind[indicator_filter]["description"])

            current_value = round(us_macro_act_data.iloc[-1].values[0], 3)
            lowest_value = round(us_macro_act_data.min().values[0], 3)
            highest_value = round(us_macro_act_data.max().values[0], 3)
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
                
                gdp_imf = self.utils.get_gdp("USA", self.hist_ind_ids[0], forward=True)
                retail_sales = self.get_usa_macro_act_indicators(ids=["RSXFS"])[0]
                gdp_atlanta = self.get_recent_gdp_forecasts()[0]
                gdp_ny = self.get_ny_gdp_forecasts()
                dgse = self.get_dsge()
            
            us_forecasts = [gdp_imf, retail_sales, gdp_atlanta, gdp_ny, dgse]
            us_macro_act_forecast = us_forecasts[self.us_macro_act_for.get(indicator_filter)]

            c1, c2, c3 = st.columns([6, .3, 3], vertical_alignment="center")
            
            options = self.utils.echart_dict(us_macro_act_forecast, label_format="%", title=indicator_filter)
            if "DSGE" in indicator_filter:
                options = self.utils.confint_chart(us_macro_act_forecast, title=indicator_filter, label_format="%")
            if "Varejo" in indicator_filter:
                options = self.utils.echart_dict(us_macro_act_forecast, title=indicator_filter)

            if coluna3.toggle("Variação Percentual"):
                formatter = "%"
                if "Varejo" in indicator_filter:
                    formatter = ""
                    us_macro_act_forecast = us_macro_act_forecast.resample("Y")
                    us_macro_act_forecast = us_macro_act_forecast.first().pct_change().dropna() * 100
                options = self.utils.bar_chart_dict(us_macro_act_forecast, title=indicator_filter)

            with c1.container():
                st.html("<span class='column_graph'></span>")
                col,_ = st.columns([10,.05])
                with col:
                    st_echarts(options=options, height="500px", theme="dark")

            with st.popover("Sobre", icon=":material/info:"):
                st.write(self.for_ind[indicator_filter]["description"])

            current_value = round(us_macro_act_forecast.iloc[-1].values[0], 3)
            if "DSGE" in indicator_filter or "FMI" in indicator_filter:
                current_value = round(us_macro_act_forecast.iloc[0].values[0], 3)
            lowest_value = round(us_macro_act_forecast.min().values[0], 3)
            highest_value = round(us_macro_act_forecast.max().values[0], 3)
            with c3:
                co1, co2, co3 = st.columns([1, 3, 1])
                st.html("<span class='indicators'></span>")
                co2.metric("Valor Atual", f"{current_value}%")
                co2.metric("Maior Valor", f"{highest_value}%")
                co2.metric("Menor Valor", f"{lowest_value}%")
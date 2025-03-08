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
import requests
from bs4 import BeautifulSoup

class SPMult:
    """S&P 500 Multiples"""

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

        self.ind = self.indicators.get_theme_dict("us_mkt_prices_hist")
        self.ind_ids = self.indicators.get_ids_list("us_mkt_prices_hist")

        self.sp_mult= dict(zip(list(self.ind.keys()), 
                               list(range(3))))
        
        
        warnings.filterwarnings('ignore')        

    
    @st.cache_data(show_spinner=False)
    def get_sp_multiples(_self) -> pd.DataFrame | tuple:
        """Scraps the S&P500
        multiples"""

        multas_base_url = _self.config.vars.mult_base_url
        mults_dict = {mult: [] for mult in _self.config.vars.sp_mult_urls}

        for mult in _self.config.vars.sp_mult_urls:

            try:
                response = requests.get(f"{multas_base_url}/{mult}", verify=False)
                if not response.ok:
                    raise FileNotFoundError(f"Unable to request the {mult}")
                
                soup = BeautifulSoup(response.content, "html.parser")
                elems = [elem.text.strip() for elem in soup.find_all("td")]
                mults_dict[mult] = elems

            except Exception as error:
                raise OSError(error) from error

        sp_ey = [round(
            float(elem.strip("†\n")[:-1])/100, 4
            ) for elem 
            in mults_dict[_self.config.vars.sp_mult_urls[0]][::-1] 
            if "%" in elem]

        sp_pe = [float(elem.strip("†\n")[:-1]) for elem 
            in mults_dict[_self.config.vars.sp_mult_urls[1]][::-1]
            if "." in elem]
        
        sp_pb = [float(elem.strip("†\n")) for elem 
                 in mults_dict[_self.config.vars.sp_mult_urls[2]][::-1] if "." in elem]
        
        index_date_ey_pe = [elem for elem 
            in mults_dict[_self.config.vars.sp_mult_urls[1]][::-1]
            if "." not in elem]
        
        index_date_pb = [elem for elem 
                 in mults_dict[_self.config.vars.sp_mult_urls[2]][::-1] if "," in elem]
        
        df_ey = pd.DataFrame({
            "Date": index_date_ey_pe, 
            "earning_yields": sp_ey,
        })

        df_ey["Date"] = pd.to_datetime(df_ey["Date"])
        df_ey["year"] = df_ey["Date"].dt.year
        df_ey.set_index("Date", inplace=True)

        df_pe = pd.DataFrame({
            "Date": index_date_ey_pe, 
            "price_earnings": sp_pe,
        })

        df_pe["Date"] = pd.to_datetime(df_pe["Date"])
        df_pe["year"] = df_pe["Date"].dt.year
        df_pe.set_index("Date", inplace=True)

        df_pb = pd.DataFrame({
            "Date": index_date_pb, 
            "price_to_book": sp_pb,
        })

        df_pb["Date"] = pd.to_datetime(df_pb["Date"])
        df_pb["year"] = df_pb["Date"].dt.year
        df_pb.set_index("Date", inplace=True)

        return df_ey, df_pe, df_pb


    def get_estimatives(self, df: pd.DataFrame):
        """Gets estimative of PE"""

        return df.iloc[-1]

    def generate_graphs(self):
        """Generates dashboard interface"""

        c1, c2, c3 = st.columns([2, .5, 1])
        coluna1, coluna2, coluna3 = c1.columns([4,1,4], vertical_alignment="center")

        with st.spinner("Carregando os dados..."):
            
            indicator_filter = c1.selectbox(
                "Selecione o múltiplo", 
                list(self.sp_mult.keys()), 
                index=0 
                )
            
            sp_mult = self.get_sp_multiples()

        sp_choose_data = sp_mult[self.sp_mult[indicator_filter]]

        sp_choose_data = sp_choose_data[sp_choose_data.index.year >= 2000]
        
        c1, c2, c3 = st.columns([6, .5, 2], vertical_alignment="center")
        
        options = self.utils.echart_dict(sp_choose_data, title=indicator_filter, mean=True)
        formatter = ""

        if "Yield" in indicator_filter:
            sp_choose_data[self.ind[indicator_filter]["id"]] = sp_choose_data[self.ind[indicator_filter]["id"]] * 100
            options = self.utils.echart_dict(sp_choose_data, label_format="%", title=indicator_filter)
            formatter = "%"
        
        with c1.container():
            st.html("<span class='column_graph'></span>")
            col,_ = st.columns([10,.05])
            with col:
                st_echarts(options, height="500px", theme="dark")

        current_value = round(sp_choose_data.iloc[-1].values[0], 3)
        lowest_value = round(sp_choose_data.min().values[0], 3)
        highest_value = round(sp_choose_data.max().values[0], 3)
        
        with c3:
            co1, co2, co3 = st.columns([1, 3, 1])
            st.html("<span class='indicators'></span>")
            co2.metric("Valor Atual", f"{current_value}{formatter}")
            co2.metric("Maior Valor", f"{highest_value}{formatter}")
            co2.metric("Menor Valor", f"{lowest_value}{formatter}")

        with c1.popover("Sobre", icon=":material/info:"):
                st.markdown(self.ind[indicator_filter]["description"], unsafe_allow_html=True)
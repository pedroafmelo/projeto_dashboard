# -*- coding: UTF-8 -*-
"""Import modules"""

from os import path, makedirs, system
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import warnings
import altair as alt
from streamlit_echarts import st_echarts
from fredapi import Fred
import yfinance as yf


class CommIndexes:
    """Commodities Indexes Global"""

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

        self.fred = Fred(self.config.vars.FRED_API_KEY)

        self.indexes_ind = self.indicators.get_theme_dict("comm_indexes")
        self.indexes_ids = self.indicators.get_ids_list("comm_indexes")

        self.comm_indexes = dict(zip(list(self.indexes_ind.keys()),
                          self.indexes_ids))
        
        
        warnings.filterwarnings('ignore')


    @st.cache_resource(show_spinner=False)
    def get_gsci_series(_self) -> pd.DataFrame:
        """Downloads GSCI etf
        series"""
        
        try:
            gsci = yf.download(_self.indicators.get_ids_list("comm_indexes")[0], start=_self.start, end=_self.end)["Close"]
        except Exception as error:
                raise OSError(error) from error

        return gsci
    
    @st.cache_resource(show_spinner=False)
    def get_all_comm_index(_self) -> pd.DataFrame:
        """Downloads all comms index"""
        
        try:
            all_comm = _self.fred.get_series(_self.indicators.get_ids_list("comm_indexes")[3], 
                                             observation_start=_self.start, 
                                             observation_end=_self.end)
            all_comm = all_comm.to_frame().dropna()
            all_comm.index.name = "Date"

        except Exception as error:
                raise OSError(error) from error
        
        return all_comm
    


    @st.cache_resource(show_spinner=False)
    def get_comm_indexes(_self) -> pd.DataFrame | list:
        """Download Commodities Indexes"""
        
        comm_list = []

        for comm_ind in _self.indexes_ids[1:3]:
            try:
                comm = _self.fred.get_series(comm_ind, observation_start=_self.start, 
                                     observation_end=_self.end)
                comm = comm.to_frame(name=comm_ind).interpolate()
                comm_list.append(comm)
            except Exception as error:
                raise OSError(error) from error
            
        df_final = pd.concat(comm_list, axis=1)
        df_final.dropna
            
        return df_final
    

    def generate_graphs(self):
        """Generates dashboard interface"""

        c1, c2, c3 = st.columns([2, .5, 1])
        coluna1, coluna2, coluna3 = c1.columns([7,2,4], vertical_alignment="center")

        with st.spinner("Carregando os dados..."):
            
            indicator_filter = coluna1.selectbox(
                " ", 
                list(self.comm_indexes.keys()), 
                index=0, key="commodities_indicator"
                )
            
            gsci_index = self.get_gsci_series()
            all_comms_index = self.get_all_comm_index()
            comm_indexes = self.get_comm_indexes()
            
            

        if "GSCI" in indicator_filter:
            choose_comm_index = gsci_index
        elif "Todas" in indicator_filter:
            choose_comm_index = all_comms_index
        elif "Brasil" in indicator_filter:
            try:
                br_indexes = self.utils.get_bcb(indicator_filter, self.comm_indexes[indicator_filter])
            except:
                st.error("Erro na requisição ao site")
            choose_comm_index = br_indexes
        else:
            choose_comm_index = comm_indexes[self.comm_indexes[indicator_filter]].to_frame()
        
        c1, c2, c3 = st.columns([6, .3, 3], vertical_alignment="center")
        
        options = self.utils.echart_dict(choose_comm_index, label_format="", title=indicator_filter)
        formatter = ""

        with c1.container():
            st.html("<span class='column_graph'></span>")
            col,_ = st.columns([10,.05])
            with col:
                st_echarts(options, height="500px", theme="dark")

        with st.popover("Sobre", icon=":material/info:"):
            st.write(self.indexes_ind[indicator_filter]["description"])

        current_value = round(choose_comm_index.iloc[-1].values[0], 3)
        lowest_value = round(choose_comm_index.min().values[0], 3)
        highest_value = round(choose_comm_index.max().values[0], 3)
        with c3:
            co1, co2, co3 = st.columns([1, 3, 1])
            st.html("<span class='indicators'></span>")
            co2.metric(f"Valor Atual", f"{round(current_value, 2)}{formatter}")
            co2.metric(f"Maior Valor", f"{round(highest_value, 2)}{formatter}")
            co2.metric(f"Menor Valor", f"{round(lowest_value, 2)}{formatter}")
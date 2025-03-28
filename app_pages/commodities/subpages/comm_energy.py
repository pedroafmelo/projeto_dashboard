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


class EnergyComm:
    """Energy Commodities Global"""

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

        self.energy_ind = self.indicators.get_theme_dict("energy_prices")
        self.energy_ids = self.indicators.get_ids_list("energy_prices")

        self.energy = dict(zip(list(self.energy_ind.keys()),
                          self.energy_ids))
        
        
        warnings.filterwarnings('ignore')


    @st.cache_resource(show_spinner=False)
    def get_energy_prices(_self) -> pd.DataFrame | list:
        """Download energy comms Prices"""
        
        comm_list = []

        for comm_ind in _self.energy_ids:
            try:
                comm = _self.fred.get_series(comm_ind, observation_start=_self.start, 
                                     observation_end=_self.end)
                comm = comm.to_frame(name=comm_ind)
                comm_list.append(comm)
            except Exception as error:
                raise OSError(error) from error
            
        df_final = pd.concat(comm_list, axis=1)
        df_final.dropna(inplace=True)
            
        return df_final


    def generate_graphs(self):
        """Generates dashboard interface"""

        c1, c2, c3 = st.columns([2, .5, 1])
        coluna1, coluna2, coluna3 = c1.columns([4,2,4], vertical_alignment="center")

        with st.spinner("Carregando os dados..."):
            
            indicator_filter = coluna1.selectbox(
                " ", 
                list(self.energy_ind.keys()), 
                index=0, key="inflation_indicator"
                )
            
            energy_data = self.get_energy_prices()
        
        energy_data_choose = energy_data[self.energy[indicator_filter]].to_frame()     
        
        c1, c2, c3 = st.columns([6, .3, 3], vertical_alignment="center")
        
        options = self.utils.echart_dict(energy_data_choose, label_format="", title=indicator_filter)
        formatter = ""

        with c1.container():
            st.html("<span class='column_graph'></span>")
            col,_ = st.columns([10,.05])
            with col:
                st_echarts(options, height="500px", theme="dark")

        with st.popover("Sobre", icon=":material/info:"):
            st.write(self.energy_ind[indicator_filter]["description"])

        current_value = round(energy_data_choose.iloc[-1].values[0], 3)
        lowest_value = round(energy_data_choose.min().values[0], 3)
        highest_value = round(energy_data_choose.max().values[0], 3)
        with c3:
            co1, co2, co3 = st.columns([1, 3, 1])
            classe = "Barril" if "Petróleo" in indicator_filter else "Milhão de BTU"
            st.html("<span class='indicators'></span>")
            co2.metric(f"Valor Atual (U$/{classe})", f"{round(current_value, 2)}{formatter}")
            co2.metric(f"Maior Valor (U$/{classe})", f"{round(highest_value, 2)}{formatter}")
            co2.metric(f"Menor Valor (U$/{classe})", f"{round(lowest_value, 2)}{formatter}")
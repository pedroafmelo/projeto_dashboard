# -*- coding: UTF-8 -*-
"""Import modules"""

from os import path, makedirs, system
import pandas as pd
from glob import glob
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
import json
from functools import reduce

class GlobalMult:
    """Global ex US Markets Multiples"""

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

        self.ind = self.indicators.get_theme_dict("global_mkt_preco")
        self.ind_ids = self.indicators.get_ids_list("global_mkt_preco")

        self.ibov_mult= dict(zip(list(self.ind.keys()), 
                               list(range(1))))
        
        warnings.filterwarnings('ignore')        



    @st.cache_resource(show_spinner=False)
    def global_markets_cover(_self):
        """Generates the Global 
        ex US cover"""
        

        col1, col2, col3 = st.columns([10.5, .5, 2])
        col1.subheader("Indicadores de Mercado - Global ex US", divider="grey")

        col3.image(path.join(_self.config.vars.img_dir, 
                            _self.config.vars.logo_bequest), width=300)

    
    @st.cache_resource(show_spinner=False)
    def get_indexes_series(_self, filename: list, list_names: list) -> pd.DataFrame:
        """Gets the Emerging Markets PE Ratio"""


        with open(path.join(_self.config.vars.data_dir,
                            filename)) as file:
            data = json.load(file)

        df_list = [pd.DataFrame({"Data": [data["series"][i][:][j][0] 
                                  for j in range(len(data["series"][i][:]))], 
                                
                                "Index": [data["series"][i][:][j][1] 
                                  for j in range(len(data["series"][i][:]))]}) 
                                  
                                  for i in range(len(data["series"]))]
        
        for index, df in enumerate(df_list):
            df = (
                df.astype({"Index": "float"})
                .rename(columns={"Index": list_names[index]})
                .set_index("Data")
            )
            df.index = pd.to_datetime(df.index)
            df_list[index] = df

        df_final = (
            reduce(lambda left, right: pd.merge(left, right, right_index=True, 
                                                       left_index=True, how="outer"), df_list)
                .fillna("temp_value").replace("temp_value", None)
        )
        
        return df_final


    def generate_graphs(self):
        """Generates dashboard interface"""

        json_list = glob(f"{self.data_dir}/*.json")
        files_list = [file.split("/")[-1] for file in json_list 
                      if "europe" in file or "asia_dev" in file]
    

        emerging = {

            "Europa": [["Alemanha", "UK", "França", "Itália", "Espanha"], files_list[1]],
            "Ásia": [["Australia", "Nova Zelândia", 
                     "Japão", "Hong Kong", "Cingapura"], files_list[0]]

        }

        c1, c2, c3 = st.columns([2, .5, 1])
        coluna1, coluna2, coluna3 = c1.columns([4,1,4], vertical_alignment="center")

        with st.spinner("Carregando os dados..."):

            indicator_filter = coluna1.selectbox(" ", list(emerging.keys()), 0)
            
            pe_data = self.get_indexes_series(emerging[indicator_filter][1], 
                                              emerging[indicator_filter][0])

        c1, c2, c3 = st.columns([6, .5, 3], vertical_alignment="center")
        
        options = self.utils.multiple_pe_chart(pe_data, legend=emerging[indicator_filter][0], 
                                               min_value=0)
        formatter = ""

        c1.markdown(f"""
                <h4 style: 'color: white'>{f"MSCI {indicator_filter} PE"}</h4>
                """, unsafe_allow_html=True)
        
        with c1.container():
            st.html("<span class='column_graph'></span>")
            col,_ = st.columns([10,.05])
            with col:
                st_echarts(options, height="500px", theme="dark")

        with c3:
                st.write(f"Valor Atual - PE")
                co1, co2 = st.columns(2)
                st.html("<span class='indicators'></span>")
                for index, col in enumerate(pe_data.columns[:len(pe_data.columns)//2]):
                    co1.metric(f"{col}", f"{round(pe_data[col].values[-1], 2)}")
                for index, col in enumerate(pe_data.columns[len(pe_data.columns)//2:]):
                    co2.metric(f"{col}", f"{round(pe_data[col].values[-1], 2)}")


        with c1.popover("Sobre", icon=":material/info:"):
                st.markdown(self.ind["P/L dos Mercados Desenvolvidos Excluindo os EUA"]["description"], unsafe_allow_html=True)
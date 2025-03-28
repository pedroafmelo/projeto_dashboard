# -*- coding: UTF-8 -*-
"""Import modules"""

from os import path, makedirs, system
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import warnings
from streamlit_echarts import st_echarts
import pandas_datareader.data as pdr
from pandas.tseries.offsets import *
from scipy import interpolate
from bs4 import BeautifulSoup
import requests
import numpy as np

class EmJuros:
    """Curva de Juros BR"""

    def __init__(self) -> None:
        """Initializes instance"""

        # import local module
        from src.iface_config import Config
        from src.indicators import Indicators
        from src.iface_extract import Extract
        from app_pages.utils import Utils
        from app_pages.usa.subpages.ffrate import UsFFR
        from src.interpolate import Interpolate

        self.config = Config()
        self.extract = Extract()
        self.indicators = Indicators()
        self.utils = Utils()
        self.ffr = UsFFR()
        self.inter = Interpolate()

        self.data_dir = self.config.vars.data_dir
        self.start = datetime(2000, 1, 1)
        self.end = datetime.today()

        self.juros = self.indicators.get_theme_dict("em_macro_juros")

        warnings.filterwarnings('ignore')    

    @st.cache_resource(show_spinner=False)
    def get_world_interest_rates(_self, continent):
        """Gets Worlds Interest Rates"""

        try:
            response = requests.get(_self.config.vars.juros_paises.replace("{continente}", continent),
                         headers=_self.config.headers)
            
            if not response.ok:
                st.error(f"Erro na requisição ao site: {_self.config.vars.juros_paises}")
            
            soup = BeautifulSoup(response.content, "html.parser")
            elems = soup.find_all("td")
            
            df = pd.DataFrame([[elems[i].text.strip() for i in range(j, len(elems), 5)] for j in range(5)]).T
            df.drop(df.columns[-1], axis=1, inplace=True)
            df.columns = ["País", "Atual", "Anterior", "Referência"]

        except Exception as error:
            raise OSError(error) from error
        
        return df
    

    @st.fragment()
    def generate_graphs(self):
        """Generates Bonds Yields Graphics"""

        continents = {
            "América": "america",
            "Europa": "europe",
            "Ásia": "asia",
            "G20": "g20"
        }

        c1, c2, c3 = st.columns([2, .5, 1])
        coluna1, coluna2, coluna3 = c1.columns([4,2,4], vertical_alignment="center")
                


        juros = [self.get_world_interest_rates(continent)
                 for continent in continents.values()]
        

        c1.markdown(
                f"""
                    <h3 style='color: white'>Taxas Básicas de Juros</h3>
                """, unsafe_allow_html=True
            )
        colunas = st.columns(4)
        
        for index, table in enumerate(juros):
            colunas[index].markdown(
                f"""
                    <h5 style='color: white'>{list(continents.keys())[index]}</h5>
                """, unsafe_allow_html=True
            )
            colunas[index].dataframe(table, hide_index=True)

        with colunas[0].popover("Sobre", icon=":material/info:"):
            st.write(self.juros["Taxas de Juros"]["description"])
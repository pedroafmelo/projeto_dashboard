# -*- coding: UTF-8 -*-
"""Import modules"""

from os import path, makedirs, system
import pandas as pd
from datetime import datetime, timedelta
import datetime as dt
import streamlit as st
import warnings
import altair as alt
import requests
import pandas_datareader.data as pdr
from streamlit_echarts import st_echarts
import numpy as np
from bs4 import BeautifulSoup
from bcb import currency
from functools import reduce


class EmRisk:
    """Emerging Markets Risk Indicators"""

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

        self.ind = self.indicators.get_theme_dict("em_macro_risco")
        self.ind_ids = self.indicators.get_ids_list("em_macro_risco")

        self.br_macro_focus = dict(zip(list(self.ind.keys()), 
                               list(range(2))))
        
        warnings.filterwarnings('ignore')


    @st.cache_resource(show_spinner=False)
    def get_adamodar_data(_self):
        """Scraps the adamodar 
        Default Spreads and Risks data"""

        def clean_list(lst, begin, step = 6):
            return [" ".join(lst[i].replace("\n", "").split()) for i in range(begin, len(lst) - (5 - begin), step)][:-1]

        try:
            response = requests.get(_self.config.vars.adamodar_url)
            if not response.ok:
                raise FileNotFoundError("Could not requets the Adamodar Data")
            soup = BeautifulSoup(response.content, "html.parser")

            elems = soup.find_all("td")

            elems = [elem.text.strip() for elem in elems]
            elems = [elem for elem in elems[elems.index("Country"):]]

        except Exception as error:
            raise OSError(error) from error
        
        countrys = clean_list(elems, 0)
        adj_default_spread = clean_list(elems, 1)
        equity_risk = clean_list(elems, 2)
        country_risk_premium = clean_list(elems, 3)
        corporate_tax_rate = clean_list(elems, 4)
        moodys = clean_list(elems, 5)

        df_adamodar = pd.DataFrame([countrys, adj_default_spread, 
                                    equity_risk, country_risk_premium,
                                    corporate_tax_rate, moodys]).T
        
        df_adamodar.columns = df_adamodar.iloc[0]
        df_adamodar.drop(0, inplace=True)

        for col in df_adamodar.columns.drop(["Country", "Moody's rating"]):
            df_adamodar[f"{col} (%)"] = df_adamodar[col].str.replace("%", "").astype(float)
            df_adamodar.drop(columns=col, inplace=True)

        ordered_cols = df_adamodar.columns.drop("Moody's rating").tolist()
        ordered_cols.append("Moody's rating")

        df_adamodar = df_adamodar[ordered_cols]

        return df_adamodar


    # Plot historical Dashboard
    @st.fragment()
    def generate_graphs(self) -> None:
        """Generates dashboard interface"""
        
        c1, c2, c3 = st.columns([4, 2, 2])

        c1.markdown("""
            <h3 style = 'color: white'>Spreads de Default e Prêmios de Risco</h3>
        """, unsafe_allow_html=True)

        risk = self.get_adamodar_data()

        st.dataframe(risk, hide_index=True)

        with st.popover("Sobre", icon=":material/info:"):
            st.write(self.ind["Default Spreads e Prêmios de Risco de países"]["description"])
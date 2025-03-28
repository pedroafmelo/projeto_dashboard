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


class GlobalAct:
    """Global ex US Markets 
    Macro Activity Indicators"""

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

        self.hist_ind = self.indicators.get_theme_dict("global_macro_act")
        self.hist_ind_ids = self.indicators.get_ids_list("global_macro_act")
        
        warnings.filterwarnings('ignore')
       

    @st.cache_resource(show_spinner=False)
    def em_macro_cover(_self):
        """Generates the global 
        ex us cover"""

        col1, col2, col3 = st.columns([10.5, .5, 2])
        col1.subheader("Indicadores Macro - Global ex US", divider="grey")

        col3.image(path.join(_self.config.vars.img_dir, 
                            _self.config.vars.logo_bequest), width=400)
        

    @st.cache_resource(show_spinner=False)
    def get_countries_pmi(_self, pmi_type):
        """Gets Countries PMI Indexes"""

        try:
            response = requests.get(_self.config.vars.pmi_paises.replace("{type}", pmi_type), 
                                    headers = _self.config.headers)
            
            if not response.ok:
                st.error("Não foi possível acessar o site - Trading Economics")

            soup = BeautifulSoup(response.content, "html.parser")
            elems = soup.find_all("td")
            data = pd.DataFrame(
                [[elems[i].text.strip() for i in range(j, len(elems), 5)] for j in range(5)]
            ).T
            data.drop(data.columns[-1], axis=1, inplace=True)
            data.columns =["País", "Último", "Anterior", "Referência"]

        except Exception as error:
            raise OSError(error) from error
        
        return data

    # Plot historical Dashboard
    @st.fragment()
    def generate_graphs(self) -> None:
        """Generates dashboard interface"""

        developed_ex_us = {
            "Alemanha": "DEU",
            "Reino Unido": "GBR",
            "França": "FRA",
            "Japão": "JPN",
            "Coreia do Sul": "KOR",
            "Itália": "ITA",
            "Espanha": "ESP",
            "Países Baixos": "NLD",
            "Suíça": "CHE",
            "Bélgica": "BEL",
            "Irlanda": "IRL",
            "Cingapura": "SGP",
        }

        
        c1, c2, c3 = st.columns([2, .5, 1])
        coluna1, coluna2, coluna3 = c1.columns([4,2,4], vertical_alignment="center")

        indicator_type = c3.selectbox(" ", ["Histórico", "Previsões"])
        if indicator_type == "Histórico":

            with st.spinner("Carregando os dados..."):
                
                indicator_filter = coluna1.selectbox(
                    " ", 
                    list(self.hist_ind.keys()),
                    index=0
                    )
                
            if "PIB" in indicator_filter:
                
                country_filter = coluna2.selectbox(
                    " ", 
                    list(developed_ex_us.keys()),
                    index=0
                    )
                
                gdp = self.utils.get_gdp(developed_ex_us[country_filter], self.hist_ind_ids[0])
                
                c1, c2, c3 = st.columns([6, .3, 3], vertical_alignment="center")
                
                options = self.utils.echart_dict(gdp, title=f"PIB Real - {country_filter}")
                formatter="%"
                
                with c1.container():
                    st.html("<span class='column_graph'></span>")
                    col,_ = st.columns([10,.05])
                    with col:
                        st_echarts(options, height="500px", theme="dark")

                with st.popover("Sobre", icon=":material/info:"):
                    st.write(self.hist_ind["PIB Real - FMI"]["description"])

                current_value = round(gdp.iloc[-1].values[0], 3)
                lowest_value = round(gdp.min().values[0], 3)
                highest_value = round(gdp.max().values[0], 3)
                with c3:
                    co1, co2, co3 = st.columns([1, 3, 1])
                    st.html("<span class='indicators'></span>")
                    co2.metric("Valor Atual", f"{current_value}{formatter}")
                    co2.metric("Maior Valor", f"{highest_value}{formatter}")
                    co2.metric("Menor Valor", f"{lowest_value}{formatter}")

            else:
                
                pmi = {"composite": "Composto",
                       "manufacturing": "Manufatura",
                       "services": "Serviços"}
                
                st.markdown(f"""
                        <h3 style='color: white; text-align: left'>PMI - Pontos</h3>
                        """, unsafe_allow_html=True)
                for index, col in enumerate(st.columns(3)):
                    col.markdown(f"""
                        <h5 style='color: white; text-align: left'>{list(pmi.values())[index]}</h5>
                        """, unsafe_allow_html=True)
                    col.dataframe(self.get_countries_pmi(list(pmi.keys())[index]), hide_index=True)

        else:
            
            with st.spinner("Carregando os dados..."):
                
                indicator_filter = coluna1.selectbox(
                    " ", 
                    list(developed_ex_us.keys()), 
                    index=0 
                    )
                
                gdp = self.utils.get_gdp(developed_ex_us[indicator_filter], self.hist_ind_ids[0], forward=True)

            c1, c2, c3 = st.columns([6, .3, 3], vertical_alignment="center")
            
            options = self.utils.echart_dict(gdp, 
                                             title=f"PIB Real - {indicator_filter}")
            formatter="%"
        
            with c1.container():
                st.html("<span class='column_graph'></span>")
                col,_ = st.columns([10,.05])
                with col:
                    st_echarts(options=options, height="500px", theme="dark")

            with st.popover("Sobre", icon=":material/info:"):
                st.write(self.hist_ind["PIB Real - FMI"]["description"])

            current_value = round(gdp.iloc[0].values[0], 3)
            lowest_value = round(gdp.min().values[0], 3)
            highest_value = round(gdp.max().values[0], 3)
            with c3:
                co1, co2, co3 = st.columns([1, 3, 1])
                st.html("<span class='indicators'></span>")
                co2.metric("Valor para ano atual", f"{current_value}{formatter}")
                co2.metric("Maior Valor", f"{highest_value}{formatter}")
                co2.metric("Menor Valor", f"{lowest_value}{formatter}")
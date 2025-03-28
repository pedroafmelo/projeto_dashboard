# -*- coding: UTF-8 -*-
"""Import modules"""

from os import path, makedirs, system
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import warnings
import altair as alt
import requests
from bs4 import BeautifulSoup
from streamlit_echarts import st_echarts
from fredapi import Fred


class GoldComm:
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

        self.fred = Fred(api_key=self.config.vars.FRED_API_KEY)

        self.gold_ind = self.indicators.get_theme_dict("gold")
        self.gold_ids = self.indicators.get_ids_list("gold")
        
        warnings.filterwarnings('ignore')

    
    @st.cache_resource(show_spinner=False)
    def comms_cover(_self):
        """Generates the S&P
         Mult cover"""
        

        col1, col2, col3 = st.columns([10.5, .5, 2])
        col1.subheader("Commodities Global", divider="grey")

        col3.image(path.join(_self.config.vars.img_dir, 
                            _self.config.vars.logo_bequest), width=300)
        
    
    @st.cache_resource(show_spinner=False)
    def get_gold_prices(_self, ouro=True):
        
        try:
            url = _self.config.vars.gold_prices if ouro == True else _self.config.vars.silver_prices
            print(url)
            response = requests.get(url,
                            headers=_self.config.headers)
                
            
            if not response.ok:
                st.error(f"Erro na requisição ao site: {_self.config.vars.gold_prices}")
        
            soup = BeautifulSoup(response.content, "html.parser")
            tabela = soup.find(id="dtDGrid")
            tabela = tabela.text.split("\n")
            data_hora = " ".join(tabela[19].split(" ")[:2])
            valor_oz = tabela[37]
            variaca_dia = tabela[27]

        except Exception as error:
            raise OSError(error) from error
        
        return data_hora, valor_oz, variaca_dia
    

    @st.cache_resource(show_spinner=False)
    def get_gold_vol_series(_self) -> pd.DataFrame:
        """Downloads gld 
        etf vol series"""

        try:
            gold_vol = _self.fred.get_series(_self.gold_ids[0], observation_start=_self.start, 
                                     observation_end=_self.end)
            gold_vol = gold_vol.to_frame().interpolate()
            gold_vol.index.name = "Date"

        except Exception as error:
                raise OSError(error) from error

        return gold_vol
    

    def generate_graphs(self):
        """Generates dashboard interface"""

        c1, c2, c3 = st.columns([6, .3, 3], vertical_alignment="center")

        with st.spinner("Carregando os dados..."):


            gold_etf_vol = self.get_gold_vol_series()
            date, gold_price, gold_var = self.get_gold_prices()
            date, silver_price, silver_var = self.get_gold_prices(ouro=False)
            
        
        options = self.utils.echart_dict(gold_etf_vol, 
                                         title="Índice de Volatilidade Implícita do Ouro")

        with c1.container():
                st.html("<span class='column_graph'></span>")
                col,_ = st.columns([10,.05])
                with col:
                    st_echarts(options, height="500px", theme="dark")

        with st.popover("Sobre", icon=":material/info:"):
            st.write(self.gold_ind["Gold Volatility Index"]["description"])

        current_value = round(gold_etf_vol.iloc[-1].values[0], 3)
        with c3:
            co1, co2, co3 = st.columns([1,4, 1])
            st.html("<span class='indicators'></span>")
            co2.html(f"Atualizado em {date}")
            co2.metric("Valor Atual do Índice", f"{current_value}")
            co2.metric("Preço atual do Ouro (U$/oz)", f"{gold_price}", delta=gold_var)
            co2.metric("Preço atual da Prata (U$/oz)", f"{silver_price}", delta=silver_var)

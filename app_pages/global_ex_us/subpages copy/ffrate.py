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
from bs4 import BeautifulSoup


class UsFFR:
    """US Macro Federal Funds Indicators"""

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

        self.ind = self.indicators.get_theme_dict("us_macro_ffr")
        self.ind_ids = self.indicators.get_ids_list("us_macro_ffr")
        
        warnings.filterwarnings('ignore')
       
        
    # Data Extraction
    @st.cache_data(show_spinner=False)
    def get_ffr_indicator(_self) -> pd.DataFrame | list:
        """Download USA Macro FFRate
          Indicators"""
            
        try:
            ind_series = pdr.DataReader(_self.ind_ids[0], "fred", _self.start, _self.end)
        except Exception as error:
            raise OSError(error) from error

        return ind_series
    
    @st.cache_resource(show_spinner=False)
    def get_meetings_list(_self):
        """Gets CME Group expectations
        about next FFRate"""

        try:

            response = requests.get(_self.config.vars.url_next_ffr_cme, 
                                    headers=_self.config.headers)
            
            if not response.ok:
                raise FileNotFoundError(f"Não foi possível requisitar o site: {_self.config.vars.url_next_ffr_cme}")
            
            soup = BeautifulSoup(response.content, "html.parser")

            datas = []
            valores = []

            for card in soup.find_all("div", class_="cardWrapper"):
                fed_info = card.find(class_="infoFed")
                data_elem = card.find(class_="percfedRateWrap")
                values = data_elem.find_all("span")
                valores.append([value.text.replace("\t", "").replace("\n", "") for value in values])
                for info in fed_info.find("i"):
                    datas.append(info)

            datas = [" ".join(data.split(" ")[:3]).replace(",", "") for data in datas]
            datas = [f"{value.split(" ")[1]} {value.split(" ")[0]} de {value.split(" ")[2]}" for value in datas]

            cme_expectations = {data:value for data, value in zip(datas, valores)}

        except Exception as error:
            raise OSError(error) from error
        
        return cme_expectations


    @st.cache_data(show_spinner=False)
    def get_cme_expectations(_self, meeting: str):

        cme_expectations = _self.get_meetings_list()
            
        try:
            
            df_filtered = pd.DataFrame({
                "Taxas": [
                    taxa for taxa in cme_expectations[meeting] if "-" in taxa
                    ], 
                "Expectativas": [
                    expec for expec in cme_expectations[meeting] if "%" in expec
                    ], 
                    })

            values = df_filtered.values
        
        except Exception as error:
            st.error("Atualize a url da CME")
        
        return values
    
    @st.cache_data(show_spinner=False)
    def get_real_natural_rate(_self):
        dsge_model = pd.read_excel(_self.config.vars.url_dsge, 
                                   sheet_name="Real Natural Rate (Percent)", 
                                   skiprows=5)
        
        dsge_model.set_index("dates", inplace=True)
        dsge_model.index = pd.to_datetime(dsge_model.index)
        dsge_model = dsge_model[dsge_model.index.year >= _self.end.year][["mean_forecast", "68.0%_lb", "68.0%_ub"]]

        return dsge_model


    # Plot historical Dashboard
    @st.fragment()
    def generate_graphs(self) -> None:
        """Generates dashboard interface"""
        
        c1, c2, c3 = st.columns([6, .3, 2.5])
        coluna1, coluna2, coluna3 = c1.columns([4,1,4], vertical_alignment="center")

        indicator_type = c3.selectbox(" ", ["Histórico", "Previsões"], key="inflation_nature", index=0)
        if indicator_type == "Histórico":

            with st.spinner("Carregando os dados..."):
                ffr_series = self.get_ffr_indicator()
            
            options = self.utils.echart_dict(ffr_series, label_format="%", title="Taxa Básica de Juros Efetiva")
            
            with c1.container():
                st.html("<span class='column_graph'></span")
                col,_ = st.columns([10,.05])
                with col:
                    st_echarts(options, height="500px", theme="dark")

            with st.popover("Sobre", icon=":material/info:"):
                st.write(self.ind["Taxa de Juros dos Fundos Federais (Federal Funds Rate)"]["description"])

            current_value = round(ffr_series.iloc[-1].values[0], 3)
            lowest_value = round(ffr_series.min().values[0], 3)
            highest_value = round(ffr_series.max().values[0], 3)
            with c3:
                st.write("#")
                co1, co2, co3 = st.columns([1, 3, 1])
                st.html("<span class='indicators'></span")
                co2.metric("Valor Atual", f"{current_value}%")
                co2.metric("Maior Valor", f"{highest_value}%")
                co2.metric("Menor Valor", f"{lowest_value}%")

        else:

            indicator_type = coluna1.selectbox(
                    "", 
                    ["Probabilidades do CME Group", "Taxa de Juros Real Natural (%) - DSGE"], 
                    index=0
                    )
            
            if indicator_type == "Probabilidades do CME Group":
            
                with st.spinner("Carregando os dados..."):

                    lista_meeting = self.get_meetings_list()
                    
                    meeting_filter = coluna3.selectbox(
                        "Selecione a data do Meeting do FED", 
                        list(lista_meeting.keys()), 
                        index=0
                        )
                    
                    values = self.get_cme_expectations(meeting_filter).tolist()

                c1, c2, c3 = st.columns([6, .5, 2], vertical_alignment="center")

                x = [value[0] for value in values]
                y = [float(value[1].replace("%", "")) for value in values]
                
                options = self.utils.simple_bar_chart_dict(x=x, y=y, title=f"Probabilidade Implícita: {meeting_filter}")

                with c1.container():
                    st.html("<span class='column_graph'></span>")
                    col,_ = st.columns([10,.05])
                    with col:
                        st_echarts(options=options, height="500px", theme="dark")

                with c3:
                    st.html("<span class='indicators'></span")
                    c3.metric("Valor Atual", f"400-425")

                with st.popover("Sobre", icon=":material/info:"):
                    st.write(self.ind["Probabilidade de Alvo da Taxa de Juros dos EUA (CME)"]["description"])

            else:

                real_natural_rate = self.get_real_natural_rate()
                options = self.utils.confint_chart(real_natural_rate, title=indicator_type)   

                with c1.container():
                    st.html("<span class='column_graph'></span>")
                    col,_ = st.columns([10,.05])
                    with col:
                        st_echarts(options=options, height="500px", theme="dark")

                trimestre_atual = round(real_natural_rate.iloc[0].values[0], 3)
                with c3:
                    st.write("#")
                    st.html("<span class='indicators'></span")
                    c3.metric("FFR Atual", f"400-425")
                    c3.metric("Previsão para o Trimestre Atual", trimestre_atual)

                with st.popover("Sobre", icon=":material/info:"):
                    st.write(self.ind["Taxa de Juros Real Natural"]["description"])
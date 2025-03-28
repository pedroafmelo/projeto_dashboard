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


class BrFocus:
    """Brasil Focus Relatory"""

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

        self.ind = self.indicators.get_theme_dict("br_macro_focus")
        self.ind_ids = self.indicators.get_ids_list("br_macro_focus")

        self.br_macro_focus = dict(zip(list(self.ind.keys()), 
                               list(range(2))))
        
        warnings.filterwarnings('ignore')


    @st.cache_data(show_spinner=False)
    def get_focus_data(_self, year: int, indicador: str):
        """Gets Focus Data"""

        dict_indicator = {
            "ipca": _self.config.vars.ipca_focus,
            "selic": _self.config.vars.selic_focus,
            "câmbio": _self.config.vars.cambio_focus,
            "pib": _self.config.vars.pib_focus
        }

        if indicador not in list(dict_indicator.keys()):
            raise OSError("Este indicador não existe na base dos relatórios Focus")

        try:
            response = requests.get(dict_indicator[indicador].replace("{data_inicial}", str(year)).replace("{data_final}", str(year)))
            if not response.ok:
                raise OSError("Não foi possível requisitar o site")
            
            data = pd.json_normalize(response.json()["value"])

            data.set_index("Data", inplace=True)
            data.index = pd.to_datetime(data.index)

            data = data[["Mediana", "DataReferencia"]]
            data["DataReferencia"] = data["DataReferencia"].astype(int)

        except Exception as error:
            raise OSError(error) from error
        
        return data
    

    @st.cache_data(show_spinner=False)
    def get_forward_focus(_self, indicador: str):
        """Gets Focus Data"""

        dict_indicator = {
            "ipca": _self.config.vars.ipca_focus,
            "selic": _self.config.vars.selic_focus,
            "câmbio": _self.config.vars.cambio_focus,
            "pib": _self.config.vars.pib_focus
        }

        if indicador not in list(dict_indicator.keys()):
            raise OSError("Este indicador não existe na base dos relatórios Focus")

        try:
            response = requests.get(dict_indicator[indicador].replace("{data_inicial}", 
                                                                      str(_self.end.year)).replace("{data_final}", 
                                                                      str(_self.end.year + 4)))
            if not response.ok:
                raise OSError("Não foi possível requisitar o site")
            
            data = pd.json_normalize(response.json()["value"])

            data.set_index("Data", inplace=True)
            data.index = pd.to_datetime(data.index)

            data = data[["Mediana", "DataReferencia"]]
            data["DataReferencia"] = data["DataReferencia"].astype(int)

            anos = sorted(data["DataReferencia"].unique()[:5])

            dados_segregados = [data[data["DataReferencia"] == ano].rename(columns={"DataReferencia": f"DataReferencia_{ano}",
                                                                                    "Mediana": f"Mediana_{ano}"}) for ano in anos]

            
            dados_final = dados_segregados[0]
            for i in range(1, len(dados_segregados)):
                dados_final = dados_final.merge(dados_segregados[i], 
                                                left_index=True,
                                                right_index=True,
                                                how="outer")
            dados_final = dados_final.fillna("temp_value").replace("temp_value", None)

        except Exception as error:
            raise OSError(error) from error
        
        return dados_final


    # Plot historical Dashboard
    @st.fragment()
    def generate_graphs(self) -> None:
        """Generates dashboard interface"""
        
        c1, c2, c3 = st.columns([2, .5, 1])
        coluna1, coluna2, coluna3 = c1.columns([4,2,4], vertical_alignment="center")

        indicator_type = c3.selectbox(" ", ["Histórico", "Previsões"], 
                                      key="inflation_nature", index=0)
        if indicator_type == "Histórico":

            with st.spinner("Carregando os dados..."):

                indicator_filter = coluna1.selectbox(" ",
                                                       ["IPCA", "PIB", "SELIC", "Câmbio"],
                                                       index=0)
                year_selector = coluna3.select_slider("Selecione o ano da relatório",
                                                 list(range(2000, self.end.year + 1)))
                # try:
                focus = self.get_focus_data(year_selector, 
                                            indicator_filter.lower())
                # except:
                #     st.error("Erro na API de dados do Banco Central")
            
            c1, c2, c3 = st.columns([6, .3, 3], vertical_alignment="center")

            dict_real_indicator = {
                "IPCA": {"IPCA": 433},
                "SELIC": {"SELIC": 432},
                "PIB": {"PIB": 433},
            }

            try:
                if indicator_filter != "Câmbio":
                    formatter = "%"
                    real_indicator_df = self.utils.get_bcb(list(dict_real_indicator[indicator_filter].keys())[0],
                                                        list(dict_real_indicator[indicator_filter].values())[0])
                    if indicator_filter != "IPCA":
                        real_indicator = real_indicator_df.resample("Y").last()
                    else:
                        real_indicator = real_indicator_df.resample("Y").apply(lambda x: (1 + x/100).prod() - 1) * 100
                    real_indicator = real_indicator[real_indicator.index.year == year_selector][indicator_filter].values[0]
                        
                else:
                    formatter = ""
                    real_indicator_df = currency.get(
                        symbols =["USD", "EUR"],
                        start= self.start,
                        end = self.end
                    )

                    real_indicator = real_indicator_df[real_indicator_df.index.year == year_selector]["USD"].values[0]
                with c3:
                    co1, co2, co3 = st.columns([1, 3, 1])
                    st.html("<span class='indicators'></span>")
                    co2.metric(f"Valor Real - {year_selector}", f"{real_indicator:.2f}{formatter}")
            except:
                    c3.error("Erro na API de dados do Banco Central")
            
            options = self.utils.echart_dict(focus, label_format=formatter, title=indicator_filter)
            
            with c1.container():
                st.html("<span class='column_graph'></span>")
                col,_ = st.columns([10,.05])
                with col:
                    st_echarts(options, height="500px", theme="dark")

            with st.popover("Sobre", icon=":material/info:"):
                st.write(self.ind["Projeções Focus"]["description"])
            

        else:

            with st.spinner("Carregando os dados..."):

                indicator_filter = coluna1.selectbox(" ",
                                                       ["IPCA", "PIB", "SELIC", "Câmbio"],
                                                       index=0)                

                focus = self.get_forward_focus(indicator_filter.lower())

            c1, c2, c3 = st.columns([6, .3, 3], vertical_alignment="center")

            formatter = "%"
            if indicator_filter == "Câmbio":
                formatter = ""
            
            options = self.utils.focus_echart(focus, 
                                             label_format=formatter, 
                                             title=indicator_filter,
                                            #  min_value=int(focus[f"Mediana_{self.end.year}"].min() - 0.5),
                                             max_value=int(focus[f"Mediana_{self.end.year}"].max() + 0.5))
            with c1.container():
                st.html("<span class='column_graph'></span>")
                col,_ = st.columns([10,.05])
                with col:
                    st_echarts(options=options, height="500px", theme="dark")

            with st.popover("Sobre", icon=":material/info:"):
                st.write(self.ind["Projeções Focus"]["description"])
            
            anos = list(range(self.end.year, self.end.year + 5))

            valores = [focus[f"Mediana_{ano}"].values[-1] for ano in anos]

            with c3:
                st.html("<span class='indicators'></span>")
                st.write("Previsão do último Focus")
                co1, co2 = st.columns([2, 2])
                for i in range(len(valores)%2 + 1):
                    co1.metric(f"{anos[i]}", f"{round(valores[i], 2)}{formatter}")
                for i in range(len(valores)%2 + 1, len(valores)):
                    co2.metric(f"{anos[i]}", f"{round(valores[i], 2)}{formatter}")
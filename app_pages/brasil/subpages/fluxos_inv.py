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
from fredapi import Fred
from bs4 import BeautifulSoup


class BrFlows:
    """US Market Financial Conditions"""

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

        self.ind = self.indicators.get_theme_dict("br_mkt_investimento")
        self.ind_ids = self.indicators.get_ids_list("br_mkt_investimento")

        self.br_fluxos_inv = list(self.ind.keys())

        self.fred = Fred(api_key=self.config.vars.FRED_API_KEY)

        warnings.filterwarnings('ignore')

    def markets_cover(self):
        """Generates the Brasil 
        Markets indicators cover"""

        col1, col2, col3 = st.columns([10.5, .5, 2])
        col1.subheader("Indicadores de Mercado - Brasil", divider="grey")

        col3.image(path.join(self.config.vars.img_dir, 
                            self.config.vars.logo_bequest), width=300)

    @st.cache_data(show_spinner=False)
    def get_b3_flows(_self) -> pd.DataFrame | list:
        """Downloads Brasil b3 
        investiment flows"""

        try:
            response = requests.get(_self.config.vars.url_b3_flows)
            if not response.ok:
                raise OSError(f"Erro na requisição ao site: Código{response.status_code}")
            soup = BeautifulSoup(response.content, "html.parser")
            elems = soup.find_all("td")

            dados = pd.DataFrame([[elems[i].text for i in range(j, len(elems), 6)] for j in range(6)]).T

            dados.columns = ["Data", 
                             "Investimento Estrangeiro", 
                             "Investimento Institucional", 
                             "Investimento Pessoa Física", 
                             "Investimento Inst. Financeira", 
                             "Investimento Outros"]

            dados["Data"] = pd.to_datetime(dados["Data"], format="%d/%m/%Y")
            dados.set_index("Data", inplace=True)

            for col in dados.columns:
                dados[col] = dados[col].map(lambda x: (
                    x.replace("mi", "")
                    .replace(".", "")
                    .replace(",", ".")
                    )).astype(float)

            dados.sort_index(inplace=True)

        except Exception as error:
            raise OSError(error) from error

        return dados

    @st.fragment()
    def generate_graphs(self) -> None:
        """Generates dashboard interface"""

        c1, c2, c3 = st.columns([4, .5, 1])
        coluna1, coluna2, coluna3 = c1.columns([6,2,4], vertical_alignment="center")

        with st.spinner("Carregando os dados..."):

            indicator_filter = coluna1.selectbox(
                " ", 
                self.br_fluxos_inv, 
                index=0 
                )

            b3_flows = self.get_b3_flows()
        b3_flows_data = b3_flows[indicator_filter].to_frame()

        c1, c2, c3 = st.columns([6, .3, 3], vertical_alignment="center")


        options = self.utils.bar_line_chart_dict(b3_flows_data, 
                                            title=indicator_filter, 
                                            min_zoom=70, 
                                            label_format=" mi")

        with c1.container():
            st.html("<span class='column_graph'></span>")
            col,_ = st.columns([10, .01])
            with col:
                st_echarts(options, height="500px", theme="dark")

        with st.popover("Sobre", icon=":material/info:"):
            st.write(self.ind[indicator_filter]["description"])

        saldo_ano = round(np.sum(b3_flows_data[b3_flows_data.index.year == self.end.year].values), 2)
        maior_valor_ano = round(np.max(b3_flows_data[b3_flows_data.index.year == self.end.year].values), 2)
        saldo_mes = round(np.sum(b3_flows_data[b3_flows_data.index.month == self.end.month].values), 2)
        maior_valor_mes = round(np.max(b3_flows_data[b3_flows_data.index.month == self.end.month].values), 2)

        with c3:
            co1, co2, co3 = st.columns([1,8,1])
            st.html("<span class='indicators'></span>")
            co2.metric("Saldo no ano", f"R$ {saldo_ano} mi")
            co2.metric("Saldo no mês", f"R$ {saldo_mes} mi")
            co2.metric("Maior valor no ano", f"{maior_valor_ano} mi")
            co2.metric("Maior valor no mês", f"{maior_valor_mes} mi")

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

class BrInf:
    """Br Macro Inflation Indicators"""

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

        self.hist_ind = self.indicators.get_theme_dict("br_macro_inf_hist")
        self.hist_ind_ids = self.indicators.get_ids_list("br_macro_inf_hist")
        self.for_ind = self.indicators.get_theme_dict("br_macro_inf_for")
        self.for_ind_ids = self.indicators.get_ids_list("br_macro_inf_for")

        self.br_macro_inf_hist= dict(zip(list(self.hist_ind.keys()), 
                               list(range(3))))
        
        self.br_macro_inf_for= dict(zip(list(self.for_ind.keys()), 
                               list(range(2))))
        
        
        warnings.filterwarnings('ignore')
    
    
    @st.cache_data(show_spinner=False)
    def get_br_implied_inflation(_self) -> str:
        """Scrap Implied Inflation
        data for specific vertices"""

        url = _self.config.vars.url_anbima_inf

        try:
            response = requests.get(url)
            if not response.ok:
                raise FileNotFoundError(f"Unable to request the AMBIMA web site")
            soup = BeautifulSoup(response.content, "html.parser")

            lista_elems = [elem.text for elem in soup.find_all("div", id="ETTJs")]
            lista_elems = [elem.replace("\n", " ").replace("\t", " ") for elem in lista_elems]
            lista_elems = lista_elems[0].split(" ")
            lista_elems = [elem for elem in lista_elems if elem not in [" ", ""]]
            lista_elems = lista_elems[lista_elems.index("Implícita") + 1:lista_elems.index("2.394") + 4]

            lista_vertices = [int(lista_elems[i].replace(".", "")) for i in range(0, len(lista_elems) - 2, 4)]
            lista_eetj_ntnb = [float(lista_elems[i].replace(",", ".")) for i in range(1, len(lista_elems) - 1, 4)]
            lista_eetj_pre = [float(lista_elems[i].replace(",", ".")) for i in range(2, len(lista_elems), 4)]
            lista_inf_implicita = [float(lista_elems[i].replace(",", ".")) for i in range(3, len(lista_elems) + 1, 4)]

        except Exception as error:
            raise OSError(error) from error
        
        df_implicita = pd.DataFrame({"Vértice": lista_vertices,
                                     "ETTJ PRE": lista_eetj_pre,
                                     "ETTJ NTNB": lista_eetj_ntnb,
                                     "Inflação Implicita": lista_inf_implicita})

        return df_implicita
    

    @st.cache_data(show_spinner=False)
    def proj_inf_bcb(_self):
        """Gets BCB inflation forecasts"""

        lista = [3, 6, 9, 12]

        atual = 3

        ano_tri = next((f"{datetime.today().year}0{mes}" 
                         for mes in lista if 1 <= (atual - mes) <= 3), 
                         f"{datetime.today().year - 1}{12}")
        
        try:
            url = _self.config.vars.relatorio_inflacao_url.replace(r"{ano_tri}", ano_tri)
            data = pd.read_excel(url, sheet_name="Graf 2.2.9", skiprows=8)
            data = data.drop(0, axis=0)
            data.set_index("Trimestre", inplace=True)
            data["Data"] = data.index.date
            data = data[["Data", "Valor Central", "Meta de inflação", "Sup da meta", "Inf da meta", 95]]
            data.columns = ["Data", "Centro da Projeção", "Meta de Inflação", "Sup da meta", "Inf da meta", "95% de Confiança"]
            data = data[data.index >= datetime.today()]

        except Exception as error:
            raise OSError(error) from error
        
        return data

    # Plot historical Dashboard
    @st.fragment()
    def generate_graphs(self) -> None:
        """Generates dashboard interface"""
        
        c1, c2, c3 = st.columns([2, .5, 1])
        coluna1, coluna2, coluna3 = c1.columns([4,2,4], vertical_alignment="center")

        indicator_type = c3.selectbox(" ", ["Histórico", "Previsões"], key="inflation_nature", index=0)
        if indicator_type == "Histórico":

            with st.spinner("Carregando os dados..."):
                
                indicator_filter = coluna1.selectbox(
                    " ", 
                    list(self.br_macro_inf_hist.keys()), 
                    index=0, key="inflation_indicator"
                    )
                
                ipca = self.utils.get_bcb("IPCA", 433)
                igpm = self.utils.get_bcb("IGPM", 189)
                ipca_ms = self.utils.get_bcb("IPCA-MS", 4466)
            
            br_macro_inf_hist = [ipca, igpm, ipca_ms]
            br_macro_inf_data = br_macro_inf_hist[self.br_macro_inf_hist[indicator_filter]]
            if coluna2.toggle("Anual", value=True, key="inflation_toggle"):
                br_macro_inf_data = br_macro_inf_data.resample("Y").apply(lambda x: (1 + x/100).prod() - 1) * 100
            
            
            c1, c2, c3 = st.columns([6, .3, 3], vertical_alignment="center")
            
            options = self.utils.echart_dict(br_macro_inf_data, label_format="%", title=indicator_filter)
            formatter = "%"
            
            if coluna3.toggle("Barras", value=True):
                formatter = "%"
                options = self.utils.bar_chart_dict(br_macro_inf_data, title=indicator_filter)
            
            with c1.container():
                st.html("<span class='column_graph'></span>")
                col,_ = st.columns([10,.05])
                with col:
                    st_echarts(options, height="500px", theme="dark")

            with st.popover("Sobre", icon=":material/info:"):
                st.write(self.hist_ind[indicator_filter]["description"])

            current_value = round(br_macro_inf_data.iloc[-1].values[0], 3)
            lowest_value = round(br_macro_inf_data.min().values[0], 3)
            highest_value = round(br_macro_inf_data.max().values[0], 3)
            with c3:
                co1, co2, co3 = st.columns([1, 3, 1])
                st.html("<span class='indicators'></span>")
                co2.metric("Valor Atual", f"{round(current_value, 2)}{formatter}")
                co2.metric("Maior Valor", f"{round(highest_value, 2)}{formatter}")
                co2.metric("Menor Valor", f"{round(lowest_value, 2)}{formatter}")

        else:

            col1, col2, col3, col4 = st.columns([4, .4, 6, .8])
            
            with st.spinner("Carregando os dados..."):
                
                inf_implicita = self.get_br_implied_inflation()
                projecao_inflacao = self.proj_inf_bcb()

            col1.markdown("""
                            <h5 style='color: white'>
                              Projeções do Banco Central do Brasil - Relatório Trimestral da Inflação  
                            </h5>
                            """, unsafe_allow_html=True)
            col1.dataframe(projecao_inflacao, hide_index=True)

            col3.markdown("""
                            <h5 style='color: white'>
                              Inflação Implícita do Brasil  
                            </h5>
                            """, unsafe_allow_html=True)
            
            table_tog = col4.toggle("Tabela")
            inf_implicita_copia = inf_implicita.copy()
            inf_implicita_copia.set_index("Vértice", inplace=True)
            
            options = self.utils.no_time_echart(inf_implicita_copia, smooth=True, label_format="%")
            if table_tog:
                col3.dataframe(inf_implicita, hide_index=True)
            
            else:
                with col3.container():
                    st.html("<span class='column_graph'></span>")
                    col,_ = st.columns([10,.05])
                    with col:
                        st_echarts(options, height="400px", theme="dark")
            
            
            with col1.popover("Sobre", icon=":material/info:"):
                st.write(self.for_ind["Projeção da Inflação - BCB"]["description"])

            with col3.popover("Sobre", icon=":material/info:"):
                st.write(self.for_ind["Inflação Implícita"]["description"])
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

class CurvaJuros:
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

        self.curvas = self.indicators.get_theme_dict("us_mkt_int_rates")
        self.lista_curvas = self.indicators.get_ids_list("us_mkt_int_rates")

        self.dic_curvas = dict(zip(list(self.curvas.keys()), 
                               list(range(3))))

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
        df_implicita.set_index("Vértice", inplace=True)

        return df_implicita
    

    @st.cache_data(show_spinner=False)
    def own_expectations(_self):
        
            lista_meetings = ["2025-01-28", "2025-03-18", 
                              "2025-05-06", "2025-06-17",
                              "2025-07-29", "2025-09-16",
                              "2025-11-04", "2025-12-09"]

            lista_datas = [datetime.strptime(data, "%Y-%m-%d") for data in lista_meetings]
            lista_datas = [data for data in lista_datas if data > datetime.today()]

            dias_proximo_meeting = [len(pd.date_range(datetime.today(), fim, 
                                                      freq=CustomBusinessDay(holidays=_self.inter.get_anbima_holidays()))) 
                                                      for fim in lista_datas]

            df = pd.DataFrame(
                    {"Próximo Meeting": [datetime.strftime(data, format="%d/%m/%Y") for data in lista_datas],
                     "Dias Úteis": dias_proximo_meeting,
                     "Cenário Positivo": [None] * len(lista_datas),
                     "Cenário Neutro": [None] * len(lista_datas),
                     "Cenário Negativo": [None] * len(lista_datas)
                     }
                     )
        
            return df
    
    
    @st.cache_data(show_spinner=False)
    def get_br_interest(_self, lista_dias):

        return _self.inter.interpolate(lista_dias)
    

    @st.fragment()
    def generate_graphs(self):
        """Generates Bonds Yields Graphics"""

        c1, c2, c3 = st.columns([2, .5, 1])
        coluna1, coluna2, coluna3 = c1.columns([4,2,4], vertical_alignment="center")


        selected_indicator = coluna1.selectbox(" ", ["Curvas de Juros",  
                                                "Expecativas Próprias"], index=0)
                

        if selected_indicator == "Curvas de Juros":

            with st.spinner("Carregando os dados..."):

                lista_dias = list(range(126, (126 * 18), 126))
                
                curva_di = self.get_br_interest(lista_dias)
        
                select_curve = coluna2.selectbox(" ", ["DI Futuro", "ETTJ Pré", "ETTJ NTNB"], index=0)

                dados = {
                    "ETTJ Pré": self.get_br_implied_inflation()["ETTJ PRE"].to_frame(),
                    "ETTJ NTNB": self.get_br_implied_inflation()["ETTJ NTNB"].to_frame(),
                    "DI Futuro": curva_di
                }

            dados_selected = dados[select_curve]

            if "Futuro" in select_curve:
                options = self.utils.multiple_interest_br(dados_selected, title = "Curva de Juros Atual", 
                                               smooth=True,
                                               min_value=round(np.min(dados_selected.values) - 1),
                                               max_value=16,
                                              marker=True,
                                              label_format="%")
                
            else:
                options = self.utils.no_time_echart(dados_selected, title=select_curve, 
                                                    column=0, label_format="%", marker=True)

            with st.container():
                st.html("<span class='column_graph'></span>")
                col,_ = st.columns([10,.05])
                with col:
                    st_echarts(options, height="500px", theme="dark")

        else:
            c1, c2 = st.columns([6, 5])
            c1.markdown(f"""
                <div style="padding-top: 0px; padding-bottom: 0px;">
                    <h4 style="margin: 0; color: white">Expectativas Próprias - Juros Brasileiros</h4>
                </div>
                """, unsafe_allow_html=True
            )

            with st.spinner("Carregando os dados..."):

                df = self.own_expectations()
                curva_di_atual = self.get_br_interest(df["Dias Úteis"].tolist())["atual"]

            with c1:
                edited_df = st.data_editor(
                    df,
                    column_config={
                        "Cenário Positivo": st.column_config.NumberColumn("Cenário Positivo", min_value=0, max_value=20),
                        "Cenário Neutro": st.column_config.NumberColumn("Cenário Neutro", min_value=0, max_value=20),
                        "Cenário Negativo": st.column_config.NumberColumn("Cenário Negativo", min_value=0, max_value=20),
                    },
                    hide_index=True
                )

            if edited_df[["Cenário Positivo", "Cenário Neutro", "Cenário Negativo"]].isnull().values.any():
                coluna1, coluna2, coluna3 = c1.columns([6,.5,4], vertical_alignment="center")
                coluna1.warning("Por favor, preencha todos os valores antes de continuar.")
            else:
                options = self.utils.multiple_4series_echart(edited_df, curva_real = curva_di_atual)

                with c2.container():
                    st.html("<span class='column_graph'></span>")
                    col,_ = st.columns([10,.05])
                    with col:
                        st.write("Curvas de Juros - Expectativas")
                        st_echarts(options, height="500px", theme="dark")

                juros_cenario_pos = round(sum(edited_df["Cenário Positivo"] * edited_df["Dias Úteis"])/(sum(edited_df["Dias Úteis"])), 2)
                juros_cenario_neutro = round(sum(edited_df["Cenário Neutro"] * edited_df["Dias Úteis"]/(sum(edited_df["Dias Úteis"]))), 2)
                juros_cenario_negativo = round(sum(edited_df["Cenário Negativo"] * edited_df["Dias Úteis"]/(sum(edited_df["Dias Úteis"]))), 2)

                with st.container():
                    co1, co2, co3 = c1.columns(3)
                    st.html("<span class='indicators'></span>")
                    co1.metric("Juros Médio - Cenário Positivo", f"{juros_cenario_pos}%")
                    co2.metric("Juros Médio - Cenário Neutro", f"{juros_cenario_neutro}%")
                    co3.metric("Juros Médio - Cenário Negativo", f"{juros_cenario_negativo}%")
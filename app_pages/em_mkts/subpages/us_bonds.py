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

class BondsYields:
    """US Bonds Yields"""

    def __init__(self) -> None:
        """Initializes instance"""

        # import local module
        from src.iface_config import Config
        from src.indicators import Indicators
        from src.iface_extract import Extract
        from app_pages.utils import Utils
        from app_pages.usa.subpages.ffrate import UsFFR

        self.config = Config()
        self.extract = Extract()
        self.indicators = Indicators()
        self.utils = Utils()
        self.ffr = UsFFR()

        self.data_dir = self.config.vars.data_dir
        self.start = datetime(2000, 1, 1)
        self.end = datetime.today()

        self.yields = self.indicators.get_theme_dict("us_mkt_int_rates")
        self.yields_list = self.indicators.get_ids_list("us_mkt_int_rates")

        warnings.filterwarnings('ignore')


    @st.cache_data(show_spinner=False)
    def get_bonds_yields(_self, yields_list) -> pd.DataFrame | list:
        """Downloads the US Gov
          Bonds Yields"""
        
        try:
            yield_series = pdr.DataReader(yields_list, "fred", _self.start, _self.end)
        except Exception as error:
            raise OSError(error) from error

        return yield_series
    
    
    @st.cache_data(show_spinner=False)
    def own_expectations(_self):
        
            lista_meetings = _self.ffr.get_meetings_list()
            lista_meet = [data.replace("de", "") for data in lista_meetings]

            lista_datas = [datetime.strptime(data.replace("de", ""), "%d %b %Y") for data in lista_meetings]

            dias_proximo_meeting = [len(pd.date_range(datetime.today(), fim, freq=BDay())) for fim in lista_datas]

            df = pd.DataFrame(
                    {"Próximo Meeting": lista_meet,
                     "Dias Úteis": dias_proximo_meeting,
                     "Cenário Positivo": [None] * len(lista_datas),
                     "Cenário Neutro": [None] * len(lista_datas),
                     "Cenário Negativo": [None] * len(lista_datas)
                     }
                     )
        
            return df

    @st.fragment()
    def generate_graphs(self):
        """Generates Bonds Yields Graphics"""

        c1, c2, c3 = st.columns([2, .5, 1])
        coluna1, coluna2, coluna3 = c1.columns([4,2,4], vertical_alignment="center")

        selected_indicator = coluna1.selectbox(" ", ["Rendimentos das Treasuries", 
                                                "Curva de Juros", 
                                                "10Y - 2Y Treasury Spread", 
                                                "Expecativas Próprias"], index=0)

        if selected_indicator == "Rendimentos das Treasuries":

            with st.spinner("Carregando os dados..."):
        
                yields_data = self.get_bonds_yields(self.yields_list[1:-1]).interpolate()

            options = self.utils.multiple_5series_echart(yields_data, title="Market Yields on U.S Treasuries")

            with st.container():
                st.html("<span class='column_graph'></span>")
                col,_ = st.columns([10,.05])
                with col:
                    st_echarts(options, height="500px", theme="dark")

            with st.popover("Sobre", icon=":material/info:"):
                st.write(self.yields["Yield de 2 anos da U.S. Treasury"]["description"])


        elif selected_indicator == "Curva de Juros":

            with st.spinner("Carregando os dados..."):
        
                yields_data = self.get_bonds_yields(self.yields_list[1:-1]).interpolate()

            now_values = yields_data.iloc[-1].values
            one_month_values = yields_data.iloc[-22].values
            three_month_values = yields_data.iloc[-64].values
            six_month_values = yields_data.iloc[-127].values
            year_month_values = yields_data.iloc[-253].values
            
            df = pd.DataFrame({"Treasury": yields_data.columns, 
                           "Atual": now_values,
                           "1 Mês": one_month_values,
                           "3 Meses": three_month_values,
                           "6 Meses": six_month_values,
                           "1 Ano": year_month_values})
            
            options = self.utils.multiple_interest(df, title = "Curva de Juros Atual", 
                                               smooth=True,
                                              marker=True)
            with st.container():
                st.html("<span class='column_graph'></span>")
                col,_ = st.columns([10,.05])
                with col:
                    st_echarts(options, height="500px", theme="dark")

        elif selected_indicator == "10Y - 2Y Treasury Spread":

            c1, c2, c3 = st.columns([6, .3, 3], vertical_alignment="center")

            spread_series = self.get_bonds_yields(self.yields_list[0]).interpolate()

            options = self.utils.echart_dict(spread_series, label_format="%", title=selected_indicator)

            with c1.container():
                st.html("<span class='column_graph'></span>")
                col,_ = st.columns([10,.05])
                with col:
                    st_echarts(options, height="500px", theme="dark")

                current_value = round(spread_series.iloc[-1].values[0], 3)
                lowest_value = round(spread_series.min().values[0], 3)
                highest_value = round(spread_series.max().values[0], 3)

                with c3:
                    co1, co2, co3 = st.columns([1, 3, 1])
                    st.html("<span class='indicators'></span>")
                    co2.metric("Valor Atual", f"{current_value}%")
                    co2.metric("Maior Valor", f"{highest_value}%")
                    co2.metric("Menor Valor", f"{lowest_value}%")

        else:

            c1, c2 = st.columns(2)

            df = self.own_expectations()

            c1.markdown(f"""
                <div style="padding-top: 0px; padding-bottom: 0px;">
                    <h4 style="margin: 0; color: white">Expectativas Próprias - Juros Americanos</h4>
                </div>
                """, unsafe_allow_html=True
            )

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

                options = self.utils.multiple_3series_echart(edited_df, title="Curva de Juros - Expectativas")
                with c2.container():
                    st.html("<span class='column_graph'></span>")
                    col,_ = st.columns([10,.05])
                    with col:
                        st_echarts(options, height="500px", theme="dark")

                juros_cenario_pos = round(sum(edited_df["Cenário Positivo"] * edited_df["Dias Úteis"])/(sum(edited_df["Dias Úteis"])), 3)
                juros_cenario_neutro = round(sum(edited_df["Cenário Neutro"] * edited_df["Dias Úteis"]/(sum(edited_df["Dias Úteis"]))), 3)
                juros_cenario_negativo = round(sum(edited_df["Cenário Negativo"] * edited_df["Dias Úteis"]/(sum(edited_df["Dias Úteis"]))), 3)


                with st.container():
                    co1, co2, co3 = c1.columns(3)
                    st.html("<span class='indicators'></span>")
                    co1.metric("Juros Médio - Cenário Positivo", f"{juros_cenario_pos}%")
                    co2.metric("Juros Médio - Cenário Neutro", f"{juros_cenario_neutro}%")
                    co3.metric("Juros Médio - Cenário Negativo", f"{juros_cenario_negativo}%")
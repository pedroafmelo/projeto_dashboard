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


class BrAct:
    """Brasil Macro Activity Indicators"""

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

        self.hist_ind = self.indicators.get_theme_dict("br_macro_act_hist")
        self.hist_ind_ids = self.indicators.get_ids_list("br_macro_act_hist")
        self.for_ind = self.indicators.get_theme_dict("br_macro_act_for")

        self.br_macro_act_hist= dict(zip(list(self.hist_ind.keys()), 
                               list(range(9))))
        
        self.br_macro_act_for= dict(zip(list(self.for_ind.keys()), 
                               list(range(2))))
        
        
        warnings.filterwarnings('ignore')
       

    @st.cache_resource(show_spinner=False)
    def br_macro_cover(_self):
        """Generates the br 
        macro cover"""

        col1, col2, col3 = st.columns([10.5, .5, 2])
        col1.subheader("Indicadores Macro - Brasil", divider="grey")

        col3.image(path.join(_self.config.vars.img_dir, 
                            _self.config.vars.logo_bequest), width=400)
        

    # Data Extraction
    @st.cache_data(show_spinner=False)
    def vendas_varejo(_self):
        """Get Brasil Retail Sales"""

        try:
            response = requests.get(_self.config.vars.vendas_varejo_url)
            if not response.ok:
                raise FileNotFoundError("Não foi possível requisitar a API SIDRA")
            
            data = pd.json_normalize(response.json())

            data = data[["D3C", "V"]]

            data["D3C"] = data["D3C"].str.slice(0,4) + "-" + data["D3C"].str.slice(4,6)
            data.rename(columns={"D3C": "Data", "V": "Vendas Varejo"}, inplace=True)
            data = data[data["Vendas Varejo"] != "..."]
            data = data.drop(0, axis=0)
            data["Vendas Varejo"] = data["Vendas Varejo"].astype(float)

            data.set_index("Data", inplace=True)

            data.index = pd.to_datetime(data.index, format="%Y-%m")
        
        except Exception as error:
            raise OSError(error) from error

        return data


    @st.cache_data(show_spinner=False)
    def prod_ind(_self):
        """Get Brasil Retail Sales"""

        lista = [3, 6, 9, 12]

        atual = 3

        ano_tri = next((f"{datetime.today().year}0{mes}" 
                         for mes in lista if 1 <= (atual - mes) <= 3), 
                         f"{datetime.today().year - 1}{12}")
        
        try:
            url = _self.config.vars.relatorio_inflacao_url.replace(r"{ano_tri}", ano_tri)
            data = pd.read_excel(url, sheet_name="C1 Boxe2 Graf 1", skiprows=8)
            data.rename(columns={"Mês": "Data", "PIM-IT": "ind_pro"}, inplace=True)
            data.set_index("Data", inplace=True)
        
        except Exception as error:
            raise OSError(error) from error

        return data
    

    @st.cache_data(show_spinner=False)
    def projecao_pib_bcb(_self):
        """Get Brasil Retail Sales"""

        lista = [3, 6, 9, 12]

        atual = 3

        ano_tri = next((f"{datetime.today().year}0{mes}" 
                         for mes in lista if 1 <= (atual - mes) <= 3), 
                         f"{datetime.today().year - 1}{12}")
        
        try:
            url = _self.config.vars.relatorio_inflacao_url.replace(r"{ano_tri}", ano_tri)

            data = pd.read_excel(url, sheet_name="C1 Boxe1 Tab 2", skiprows=6)

            for col in data.columns:
                if sum(data[col].isna())/len(data) >= 0.8:
                    data.drop(columns=col, inplace=True)

            data.columns = [col.strip(" ")[:4] if col.strip(" ") != "Discriminação" else col.strip(" ") for col in data.columns]
            data.rename(columns={"Unna": "Atual"}, inplace=True)
            data_target = data.query("Discriminação == ' PIB a preços de mercado'")[[str(_self.end.year), "Atual"]]
            data_target.columns = ["Projeção Anterior", "Projeção Atual"]
        except Exception as error:
            raise OSError(error) from error

        return data_target


    # Plot historical Dashboard
    @st.fragment()
    def generate_graphs(self) -> None:
        """Generates dashboard interface"""
        
        c1, c2, c3 = st.columns([2, .5, 1])
        coluna1, coluna2, coluna3 = c1.columns([4,2,4], vertical_alignment="center")

        indicator_type = c3.selectbox(" ", ["Histórico", "Previsões"])
        if indicator_type == "Histórico":

            with st.spinner("Carregando os dados..."):
                
                indicator_filter = coluna1.selectbox(
                    " ", 
                    list(self.br_macro_act_hist.keys()),
                    index=0
                    )
                
                gdp = self.utils.get_gdp("BRA", self.hist_ind_ids[0])
                ibcbr = self.utils.get_bcb("IBC-Br", 24364)
                prod_ind = self.prod_ind()
                vendas_var = self.vendas_varejo()
                inec_corrente = self.utils.get_bcb("INEC-Corrente", 7345)
                inec_compras = self.utils.get_bcb("INEC-Compras", 7346)
                inec_renda_pessoal = self.utils.get_bcb("INEC-Renda Pessoal", 7347)
                icei_condicoes = self.utils.get_bcb("INEC-Condições", 7342)

                br_act_ind = [
                    gdp, ibcbr, prod_ind,
                    vendas_var, inec_corrente, inec_compras,
                    inec_renda_pessoal, icei_condicoes
                ]
            
                br_macro_act_data = br_act_ind[self.br_macro_act_hist.get(indicator_filter)]
                if coluna2.toggle("Anual", value=True):
                    br_macro_act_data = br_macro_act_data.resample("Y").first()
                
            c1, c2, c3 = st.columns([6, .3, 3], vertical_alignment="center")
            
            if indicator_filter not in ["PIB Real - FMI", "Vendas no Varejo"]:
                options = self.utils.echart_dict(br_macro_act_data, title=indicator_filter)
                formatter = ""
            else:
                options = self.utils.echart_dict(br_macro_act_data, label_format="%", title=indicator_filter)
                formatter = "%"
            
            if coluna3.toggle("Variação Percentual"):
                formatter = "%"
                if indicator_filter != "PIB Real - FMI":
                    br_macro_act_data = round(br_macro_act_data.pct_change().dropna(), 3) * 100
                options = self.utils.bar_chart_dict(br_macro_act_data, title=indicator_filter)
            
            with c1.container():
                st.html("<span class='column_graph'></span>")
                col,_ = st.columns([10,.05])
                with col:
                    st_echarts(options, height="500px", theme="dark")

            with st.popover("Sobre", icon=":material/info:"):
                st.write(self.hist_ind[indicator_filter]["description"])

            current_value = round(br_macro_act_data.iloc[-1].values[0], 3)
            lowest_value = round(br_macro_act_data.min().values[0], 3)
            highest_value = round(br_macro_act_data.max().values[0], 3)
            with c3:
                co1, co2, co3 = st.columns([1, 3, 1])
                st.html("<span class='indicators'></span>")
                co2.metric("Valor Atual", f"{current_value}{formatter}")
                co2.metric("Maior Valor", f"{highest_value}{formatter}")
                co2.metric("Menor Valor", f"{lowest_value}{formatter}")

        else:
            
            with st.spinner("Carregando os dados..."):
                
                indicator_filter = coluna1.selectbox(
                    " ", 
                    list(self.br_macro_act_for.keys()), 
                    index=0 
                    )
                
                gdp_imf = self.utils.get_gdp("BRA", self.hist_ind_ids[0], forward=True)
                pib_bcb = self.projecao_pib_bcb()
                icei_expectativas = self.utils.get_bcb("INEC-Expectativas", 7343)
            
            
            br_act_forecasts = [gdp_imf, icei_expectativas]
            br_act_forecasts = br_act_forecasts[self.br_macro_act_for.get(indicator_filter)]
            if coluna2.toggle("Anual", value=True):
                    br_act_forecasts = br_act_forecasts.resample("Y").first()

            c1, c2, c3 = st.columns([6, .3, 3], vertical_alignment="center")
            
            formatter = "%"
            if "Confiança" in indicator_filter:
                    formatter = ""
            options = self.utils.echart_dict(br_act_forecasts, 
                                             label_format=formatter, 
                                             title=indicator_filter)
            

            if coluna3.toggle("Variação Percentual"):
                formatter = "%"
                if "Confiança" in indicator_filter:
                    formatter = ""
                    br_act_forecasts = br_act_forecasts.first().pct_change().dropna() * 100
                options = self.utils.bar_chart_dict(br_act_forecasts, title=indicator_filter)
            with c1.container():
                st.html("<span class='column_graph'></span>")
                col,_ = st.columns([10,.05])
                with col:
                    st_echarts(options=options, height="500px", theme="dark")

            with st.popover("Sobre", icon=":material/info:"):
                st.write(self.for_ind[indicator_filter]["description"])

            current_value = round(br_act_forecasts.iloc[-1].values[0], 3)
            lowest_value = round(br_act_forecasts.min().values[0], 3)
            highest_value = round(br_act_forecasts.max().values[0], 3)
            with c3:
                co1, co2, co3 = st.columns([1, 3, 1])
                st.html("<span class='indicators'></span>")
                co2.metric("Valor Atual", f"{current_value}{formatter}")
                co2.metric("Maior Valor", f"{highest_value}{formatter}")
                co2.metric("Menor Valor", f"{lowest_value}{formatter}")


                st.markdown("""
                            <h5 style='color: white'>
                              Projeções do Banco Central do Brasil - Relatório Trimestral da Inflação  
                            </h5>
                            """, unsafe_allow_html=True)
                c1, c2 = st.columns([2, 2])
                anterior = pib_bcb.values[0][0]
                atual = pib_bcb.values[0][1]
                c1.metric("Projeção Anterior", f"{anterior}")
                c2.metric("Projeção Atual", f"{atual}")
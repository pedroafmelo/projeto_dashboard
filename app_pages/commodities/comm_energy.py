# -*- coding: UTF-8 -*-
"""Import modules"""

from os import path, makedirs, system
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import warnings
import altair as alt


class Comm:
    """Commodities Global"""

    def __init__(self) -> None:
        """Initializes instance"""

        # import local module
        from src.iface_config import Config
        from src.iface_extract import Extract
        from src.indicators import Indicators

        self.config = Config()
        self.extract = Extract()
        self.indicators = Indicators()

        self.data_dir = self.config.vars.data_dir
        self.start = datetime(2000, 1, 1)
        self.end = datetime.today()

        self.energy_prices = self.indicators.get_theme_dict("energy_prices")
        
        warnings.filterwarnings('ignore')

    
    def comm_cover(self):
        """Generates the Global
         Commodities cover"""

        st.image(path.join(self.config.vars.img_dir, 
                           self.config.vars.logo_bequest), width=350)
                
        st.markdown("""
                <style>
                [data-baseweb = "tag"] {
                    color: black;
                }
                </style>
                <div style="padding-top: 0px; padding-bottom: 0px;">
                    <h1 style="margin: 0; color: white">Commodities Global - Grãos</h1>
                </div>
                    
                """, unsafe_allow_html=True
            )
        
        st.markdown("""<hr style="height:2px;border:none;color:blue;background-color:#faba19;" /> """,
                        unsafe_allow_html=True)
        
    
    @st.cache_data(show_spinner=False)
    def get_data(_self):
        
        return (_self.extract.get_grain_prices(),
                 _self.extract.get_energy_prices(), 
                 _self.extract.get_comm_indexes(),
                 _self.extract.get_gold_vol_series(),
                 _self.extract.get_soy_series(),
                 _self.extract.get_gsci_series(),
        )


    def generate_graphs(self):
        """Generates dashboard interface"""

        self.comm_cover()

        c1, c2, c3 = st.columns([4, .5, 3])

        with st.spinner("Carregando os dados..."):
        
            grain_prices, energy_prices, comm_indexes, gold_vol, soy, gsci, all_comm = self.get_data()    
            
        indicator_filter = c1.selectbox(
            "Selecione Grão", 
            list(self.grain_prices.keys()), 
            index=0 
            )

        year_filter = c3.slider("Selecione uma data inicial", 
                                min_value=2000,
                                max_value=datetime.today().year)
        
        c1.markdown(f"""
            <div style="padding-top: 0px; padding-bottom: 0px;">
                <h4 style="margin: 0; color: white">Commodities - {indicator_filter} (U$/Ton)</h4>
            </div>
            """, unsafe_allow_html=True
        )

        if indicator_filter == "Preço Global - Soja":

            soy_choose = soy[soy.index.year >= year_filter]
            c1.line_chart(soy_choose, color=self.config.base_color)
            c3.markdown(f"""
                <div style="padding-top: 0px; padding-bottom: 0px;">
                    <h4 style="margin: 0; color: white">{indicator_filter} - \nPreço do último trimestre (U$/Ton)</h4>
                </div>
                """, unsafe_allow_html=True
            )
            col1, col2, col3 = c3.columns([1.5, 3, 2])
            col2.write("#")
            col2.metric("Valor", 
                round(soy_choose.iloc[-1].item(), 2), 
                delta=round((soy_choose.iloc[-1] - soy_choose.iloc[-2]).item(), 2),
                border=True)
            
        else:
            grain_prices_choose = grain_prices[self.grain_prices[indicator_filter]["id"]]
            grain_prices_choose = grain_prices_choose[grain_prices_choose.index.year >= year_filter]
            c1.line_chart(grain_prices_choose, color=self.config.base_color)
            c3.markdown(f"""
                <div style="padding-top: 0px; padding-bottom: 0px;">
                    <h4 style="margin: 0; color: white">{indicator_filter} - \nPreço do último mês (U$/Ton)</h4>
                </div>
                """, unsafe_allow_html=True
            )
            col1, col2, col3 = c3.columns([1.5, 3, 2])
            col2.write("#")
            col2.metric("Valor", 
                        round(grain_prices_choose.iloc[-1], 2), 
                        delta=round((grain_prices_choose.iloc[-1] - grain_prices_choose.iloc[-2]), 2),
                        border=True)
            
        
        c1, c2, c3 = st.columns([3, .5, 4])

        c1.write("#")
        c3.write("#")
        
        indicator_filter_energy = c3.selectbox(
            "Selecione a fonte de energia", 
            list(self.energy_prices.keys()), 
            index=0 
            )
        
        c3.markdown(f"""
            <div style="padding-top: 0px; padding-bottom: 0px;">
                <h4 style="margin: 0; color: white">Commodities - {indicator_filter_energy}</h4>
            </div>
            """, unsafe_allow_html=True
        )

        energy_prices_choose = energy_prices[self.energy_prices[indicator_filter_energy]["id"]]
        energy_prices_choose = energy_prices_choose[energy_prices_choose.index.year >= year_filter]
        c3.line_chart(energy_prices_choose, color=self.config.base_color)
        if indicator_filter_energy == "Preços de Fontes de Energia - Gás Natural":
            c1.markdown(f"""
                <div style="padding-top: 0px; padding-bottom: 0px;">
                    <h4 style="margin: 0; color: white">{indicator_filter_energy} - \n Último Preço (U$/Milhão de BTU)</h4>
                </div>
                """, unsafe_allow_html=True
            )
        else:
            c1.markdown(f"""
                <div style="padding-top: 0px; padding-bottom: 0px;">
                    <h4 style="margin: 0; color: white">{indicator_filter_energy} - \n Último Preço (U$/Barril)</h4>
                </div>
                """, unsafe_allow_html=True
            )
        col1, col2, col3 = c1.columns([1.5, 3, 2])
        col2.write("#")
        col2.metric("Valor", 
            round(energy_prices_choose.iloc[-1].item(), 2), 
            delta=round((energy_prices_choose.iloc[-1] - energy_prices_choose.iloc[-2]).item(), 2),
            border=True)
        

        c1, c2, c3 = st.columns([4, .5, 4])
        
        indicator_filter_index = c1.selectbox(
            "Selecione o Índice de Commodities", 
            list(self.comm_indexes.keys()), 
            index=0 
            )
        
        c1.markdown(f"""
            <div style="padding-top: 0px; padding-bottom: 0px;">
                <h4 style="margin: 0; color: white">Commodities - {indicator_filter_index}</h4>
            </div>
            """, unsafe_allow_html=True
        )

        if indicator_filter_index == "Índice S&P GSCI": 
            if len(gsci) <= 5:
                c1.error("Erro na API de dados")
            else:
                gsci_choose = gsci[gsci.index.year >= year_filter]
                c1.line_chart(gsci_choose, color=self.config.base_color)
            
        elif indicator_filter_index == "Índice Global de Preços de Todas as Commodities":
            all_comm_choose = all_comm[all_comm.index.year >= year_filter]
            c1.line_chart(all_comm_choose, color=self.config.base_color)


        else:
            comm_indexes_choose = comm_indexes[self.comm_indexes[indicator_filter_index]["id"]]
            comm_indexes_choose = comm_indexes_choose[comm_indexes_choose.index.year >= year_filter]
            c1.line_chart(comm_indexes_choose, color=self.config.base_color)

        with c1.popover("Sobre", icon=":material/info:"):
            st.write(self.comm_indexes[indicator_filter_index]["description"])

        c3.write("#")
        c3.markdown("""
            <div style="padding-top: 0px; padding-bottom: 0px;">
                    <h4 style="margin: 0; color: white"> Índice de Volatilidade Implícita do ETF GLD</h4>
            </div>
            """, unsafe_allow_html=True)
        
        c3.line_chart(gold_vol, color=self.config.base_color)


comm = Comm()
comm.generate_graphs()
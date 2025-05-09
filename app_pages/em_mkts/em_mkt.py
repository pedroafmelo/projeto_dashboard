# -*- coding: UTF-8 -*-
"""Import modules"""

from os import path, makedirs, system
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import warnings
import altair as alt
import time
import asyncio


class EmMkt:
    """Emergin Markets Indicators"""

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

        self.em_indicators = self.indicators.get_theme_dict("emerging_markets")
        
        warnings.filterwarnings('ignore')

    
    def em_mkt_cover(self):
        """Generates the em_mkt
        cover"""

        st.image(path.join(self.config.vars.img_dir, 
                           self.config.vars.logo_bequest), width=350)
                
        st.markdown("""
                <style>
                [data-baseweb = "tag"] {
                    color: black;
                }
                </style>
                <div style="padding-top: 0px; padding-bottom: 0px;">
                    <h1 style="margin: 0; color: white">Indicadores de Mercados Emergentes</h1>
                </div>
                    
                """, unsafe_allow_html=True
            )
        
        st.markdown("""<hr style="height:2px;border:none;color:blue;background-color:#faba19;" /> """,
                        unsafe_allow_html=True)


    @st.cache_data(show_spinner=False)
    def get_data(_self):

        return _self.extract.get_emerging_data(), _self.extract.get_emb_series(), _self.extract.get_vxeem()
    

    def generate_graphs(self) -> None:
        """Generates dashboard interface"""
        
        self.em_mkt_cover()

        c1, c2, c3 = st.columns([4, .5, 3])

        with st.spinner("Carregando os dados..."):
            
            indicator_filter = c1.selectbox(
                "Selecione o indicador de mercados emergentes", 
                list(self.em_indicators.keys()),
                index=0 
                )

            year_filter = c3.slider("Selecione uma data inicial", 
                                min_value=2000,
                                max_value=datetime.today().year)
            
            em_mkt_data, emb, vxeem = self.get_data()
            em_mkt_data_choose = em_mkt_data[self.em_indicators[indicator_filter]["id"]]
            em_mkt_data_choose = em_mkt_data_choose[em_mkt_data_choose.index.year >= year_filter]

        c1.markdown(f"""
            <div style="padding-top: 0px; padding-bottom: 0px;">
                <h4 style="margin: 0; color: white">Mercados Emergentes - {indicator_filter}</h4>
            </div>
                
            """, unsafe_allow_html=True
        )

        st.line_chart(em_mkt_data_choose, color=self.config.base_color)

        with st.popover("Sobre", icon=":material/info:"):
            st.write(self.em_indicators[indicator_filter]["description"])

        c1, c2, c3 = st.columns([4, .25, 3])

        c1.markdown(f"""
            <div style="padding-top: 0px; padding-bottom: 0px;">
                <h4 style="margin: 0; color: white">Série Histórica - Emerging Markets ETF volatility (VXEEM)</h4>
            </div>
                
            """, unsafe_allow_html=True
        )

        c1.line_chart(vxeem, color=self.config.base_color)

        with c1.popover("Sobre", icon=":material/info:"):
            st.write(self.indicators.all_dict["em_etfs_vol"]["description"])

        c3.markdown(f"""
            <div style="padding-top: 0px; padding-bottom: 0px;">
                <h4 style="margin: 0; color: white">Série Histórica de Preços - ETF EMB (U$)</h4>
            </div>
                
            """, unsafe_allow_html=True
        )

        if len(emb) == 0:
            c3.error("Erro na API de dados")

        c3.line_chart(emb, color=self.config.base_color)

        with c3.popover("Sobre", icon=":material/info:"):
            st.write(self.indicators.all_dict["emb"]["description"])

em_mkt = EmMkt()
em_mkt.generate_graphs()
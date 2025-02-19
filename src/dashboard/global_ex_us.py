# -*- coding: UTF-8 -*-
"""Import modules"""

from os import path, makedirs, system
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import warnings
import altair as alt


class GlobalExUS:
    """GlobalExUS"""

    def __init__(self) -> None:
        """Initializes instance"""

        # import local module
        from src.iface_config import Config
        from src.iface_extract import Extract

        self.config = Config()
        self.extract = Extract()

        self.data_dir = self.config.vars.data_dir
        self.start = datetime(2000, 1, 1)
        self.end = datetime.today()

        warnings.filterwarnings('ignore')

    
    def geu_cover(self):
        """Generates the us 
        bonds cover"""

        
        st.image(path.join(self.config.vars.img_dir, 
                           self.config.vars.logo_bequest))
                
        st.markdown("""
                    
                <style>
                [data-baseweb = "tag"] {
                    color: black;
                }
                </style>

                <div style="padding-top: 0px; padding-bottom: 0px;">
                    <h1 style="margin: 0; color: white">Global Ex US</h1>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("""<hr style="height:2px;border:none;color:blue;background-color:#faba19;" /> """,
                        unsafe_allow_html=True)


    @st.cache_data(show_spinner=False)
    def get_data(_self):

        return _self.extract.get_global_exus_data(), _self.extract.get_adamodar_data()


    def generate_graphs(self):
        """Generates Bonds Yields Graphics"""

        self.geu_cover()

        c1, c2, c3 = st.columns([2, .5, 3])

        with st.spinner("Carregando os dados..."):

            year_filter = c1.slider("Selecione uma data inicial", 
                                min_value=2008,
                                max_value=datetime.today().year)
            
            global_data, adamodar_data = self.get_data()

        st.markdown("""
            <div style="padding-top: 0px; padding-bottom: 0px;">
                    <h4 style="margin: 0; color: white"> Série Histórica de Preços- ETF SPDW (U$)</h4>
            </div>
            """, unsafe_allow_html=True)
        
        if len(global_data) == 0:
            c1.error("Erro na API de dados")
        global_data_choose = global_data[global_data.index.year >= year_filter]

        st.line_chart(global_data_choose, color=self.config.base_color)


        st.markdown(f"""
                <div style="padding-top: 0px; padding-bottom: 0px;">
                    <h4 style="margin: 0; color: white">Country Default Spreads and Risk Premiums </h4>
                </div>
                    
                """, unsafe_allow_html=True
            )
        st.dataframe(adamodar_data, hide_index=True)
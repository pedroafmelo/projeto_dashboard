# -*- coding: UTF-8 -*-
"""Import modules"""

from os import path, makedirs, system
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import warnings
import altair as alt


class BondsYields:
    """Extract Interface"""

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

        yields = [
            "Yield de 2 anos da U.S Treasury",
            "Yield de 5 anos da U.S Treasury",
            "Yield de 10 anos da U.S Treasury",
            "Yield de 20 anos da U.S Treasury",
            "Yield de 30 anos da U.S Treasury"
        ]

        self.yields = dict(zip(yields, 
                               self.config.vars.us_bonds_yields))

        warnings.filterwarnings('ignore')

    
    def yields_cover(self):
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
                    <h1 style="margin: 0; color: white">US Bonds Yields</h1>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("""<hr style="height:2px;border:none;color:blue;background-color:#faba19;" /> """,
                        unsafe_allow_html=True)


    @st.cache_data(show_spinner=False)
    def get_data(_self):

        return _self.extract.get_bonds_yields()


    def generate_graphs(self):
        """Generates Bonds Yields Graphics"""


        self.yields_cover()

        c1, c2, c3 = st.columns([4, .5, 3])

        with st.spinner("Carregando os dados..."):
            yields_list = c1.multiselect(
                "Selecione as Treasuries Yields", 
                list(self.yields.keys()), 
                default=[list(self.yields.keys())[0]]  
                )
        
            yields_filter = [self.yields.get(chave) for chave in yields_list]

            year_filter = c3.slider("Selecione uma data inicial", 
                                min_value=2000,
                                max_value=datetime.today().year)
            
            yields_data = self.get_data()[yields_filter]
            yields_data = yields_data[yields_data.index.year >= year_filter]

        colors = ["#ffffff", "#dd4f00", "#983f4a", "#ffae42", "#ffba6a"]

        st.write("#")

        st.line_chart(yields_data, color = colors[:len(yields_filter)])
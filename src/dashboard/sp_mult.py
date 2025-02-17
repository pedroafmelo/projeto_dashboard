# -*- coding: UTF-8 -*-
"""Import modules"""

from os import path, makedirs, system
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import warnings
import altair as alt


class SPMult:
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

        indicators = [
            "S&P 500 Earning Yields",
            "S&P 500 Price/Earnings",
            "S&P 500 Price-to-Book",
        ]
        self.mult_ind = dict(zip(indicators, 
                               [
                                   "earning_yields",
                                   "price_earnings",
                                   "price_to_book"
                               ]))
        
        warnings.filterwarnings('ignore')

    
    def sp_mult_cover(self):
        """Generates the S&P
         Mult cover"""

        st.image(path.join(self.config.vars.img_dir, 
                           self.config.vars.logo_bequest))
                
        st.markdown("""
                <style>
                [data-baseweb = "tag"] {
                    color: black;
                }
                </style>
                <div style="padding-top: 0px; padding-bottom: 0px;">
                    <h1 style="margin: 0; color: white">Múltiplos S&P 500</h1>
                </div>
                    
                """, unsafe_allow_html=True
            )
        
        st.markdown("""<hr style="height:2px;border:none;color:blue;background-color:#faba19;" /> """,
                        unsafe_allow_html=True)
        
    
    @st.cache_data(show_spinner=False)
    def get_data(_self):

        sp_ey_pe, sp_pb = _self.extract.get_sp_multiples()

        sp_ey_pe = sp_ey_pe[:-1]
        sp_pb = sp_pb[:-1]

        return sp_ey_pe, sp_pb

    
    def get_estimatives(self, df: pd.DataFrame):
        """Gets estimative of PE"""

        return df.iloc[-1]

    def generate_graphs(self):
        """Generates dashboard interface"""

        self.sp_mult_cover()

        c1, c2, c3 = st.columns([4, .5, 3])

        with st.spinner("Carregando os dados..."):
            
            indicator_filter = c1.selectbox(
                "Selecione o múltiplo", 
                list(self.mult_ind.keys()), 
                index=0 
                )

            year_filter = c3.slider("Selecione uma data inicial", 
                                min_value=2000,
                                max_value=datetime.today().year)
            
            sp_ey_pe, sp_pb = self.get_data()

        c1, c2, c3 = st.columns([5, .5, 2])
        
        c1.markdown(f"""
            <div style="padding-top: 0px; padding-bottom: 0px;">
                <h4 style="margin: 0; color: white">US Market Indicators - {indicator_filter}</h4>
            </div>
            """, unsafe_allow_html=True
        )

        if indicator_filter == "S&P 500 Price-to-Book":
            estimative_pb = self.get_estimatives(sp_pb)
            sp_pb = sp_pb[sp_pb["year"] >= year_filter]
            c1.line_chart(sp_pb, y = "price_to_book", color="#fba725")
            c3.markdown(f"""
            <div style="padding-top: 0px; padding-bottom: 0px;">
                <h4 style="margin: 0; color: white">Estimativa - {indicator_filter} - {estimative_pb.name.date}</h4>
            </div>
            """, unsafe_allow_html=True
        )
            col1, col2, col3 = c3.columns(3)
            col2.write("#")
            col2.metric("Valor", 
                        estimative_pb[self.mult_ind.get(indicator_filter)], 
                        delta = sp_pb.iloc[-2]["price_to_book"],
                        border=True)
        
        else:
            sp_ey_pe_choose = sp_ey_pe[[self.mult_ind.get(indicator_filter), "year"]]
            sp_ey_pe_choose = sp_ey_pe_choose[sp_ey_pe_choose["year"] >= year_filter][self.mult_ind.get(indicator_filter)]
            estimative_ey_pe = self.get_estimatives(sp_ey_pe)
            c1.line_chart(sp_ey_pe_choose, color="#fba725")
            c3.markdown(f"""
            <div style="padding-top: 0px; padding-bottom: 0px;">
                <h4 style="margin: 0; color: white">Estimativa - {indicator_filter} - {estimative_ey_pe.name.date}</h4>
            </div>
            """, unsafe_allow_html=True
        )
            col1, col2, col3 = c3.columns([1.5, 3, 2])
            col2.write("#")
            col2.metric("Valor", 
                        estimative_ey_pe[self.mult_ind.get(indicator_filter)], 
                        delta = sp_ey_pe_choose.iloc[-2],
                        border=True)


       
# -*- coding: UTF-8 -*-
"""Import modules"""

from os import path, makedirs, system
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import warnings
import altair as alt


class UsMkt:
    """US Market Indicators"""

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
            "Spread de Liquidez (Treasury Bill de 3 meses menos FFR)",
            "ICE BofA US High Yield Index Option-Adjusted Spread",
            "ICE BofA US Corporate Index Option-Adjusted Spread",
            "Índice de Condição Financeira - FED de Chicago FCI",
            "Sub-Índice de Alavancagem do FCI",
            "Sub-Índice de Risco do FCI",
            "Sub-Índice de Crédito do FCI"
        ]
        self.mkt_ind = dict(zip(indicators, 
                               list(range(7))))
        
        warnings.filterwarnings('ignore')

    
    def us_mkt_cover(self):
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
                    <h1 style="margin: 0; color: white">US Market Indicators</h1>
                </div>
                    
                """, unsafe_allow_html=True
            )
        
        st.markdown("""<hr style="height:2px;border:none;color:blue;background-color:#faba19;" /> """,
                        unsafe_allow_html=True)
        
    
    @st.cache_data(show_spinner=False)
    def get_data(_self):

        return _self.extract.get_market_indicators(),  _self.extract.get_dxy_series(), _self.extract.get_mkt_returns()


    def generate_graphs(self):
        """Generates dashboard interface"""

        self.us_mkt_cover()

        c1, c2, c3 = st.columns([4, .5, 3])

        with st.spinner("Carregando os dados..."):
            
            indicator_filter = c1.selectbox(
                "Selecione o indicador de mercado", 
                list(self.mkt_ind.keys()), 
                index=0 
                )

            year_filter = c3.slider("Selecione uma data inicial", 
                                min_value=2000,
                                max_value=datetime.today().year)
            
            us_mkt_data, dxy, ff_returns = self.get_data()
            us_mkt_data_choose = us_mkt_data[self.mkt_ind.get(indicator_filter)]
            us_mkt_data_choose = us_mkt_data_choose[us_mkt_data_choose.index.year >= year_filter]
            if len(dxy) <=5:
                c1.error("Erro na API de dados")
            else:
                dxy = dxy[dxy.index.year >= year_filter]
            ff_returns = ff_returns[ff_returns.index.year >= year_filter]
    
        c1.markdown(f"""
            <div style="padding-top: 0px; padding-bottom: 0px;">
                <h4 style="margin: 0; color: white">US Market Indicators - {indicator_filter}</h4>
            </div>
            """, unsafe_allow_html=True
        )

        st.line_chart(us_mkt_data_choose, color=self.config.base_color)

        c1, c2, c3 = st.columns([4, .5, 3])

        c1.markdown(f"""
            <div style="padding-top: 0px; padding-bottom: 0px;">
                <h4 style="margin: 0; color: white">Índice do Dólar - DXY</h4>
            </div>
                
            """, unsafe_allow_html=True
        )
        if len(dxy) <=5:
            c1.error("Erro na API de dados")
        else:
            c1.line_chart(dxy, color="#ffae42")

        c3.markdown(f"""
            <div style="padding-top: 0px; padding-bottom: 0px;">
                <h4 style="margin: 0; color: white">Retorno Líquido do Mercado Acionário</h4>
            </div>
                
            """, unsafe_allow_html=True
        )
        
        c3.line_chart(ff_returns, color="#ffae42")
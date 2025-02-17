# -*- coding: UTF-8 -*-
"""Import modules"""

from os import path, makedirs, system
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import warnings
import altair as alt


class UsEco:
    """US Economic Indicators"""

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
            "Produção Industrial",
            "CPI - Urbano",
            "PCE",
            "Inflação Implícita de 5 anos"
        ]
        self.eco_ind = dict(zip(indicators, 
                               list(range(6))))
        
        warnings.filterwarnings('ignore')

    
    def us_eco_cover(self):
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
                    <h1 style="margin: 0; color: white">US Economic Indicators</h1>
                </div>
                    
                """, unsafe_allow_html=True
            )
        
        st.markdown("""<hr style="height:2px;border:none;color:blue;background-color:#faba19;" /> """,
                        unsafe_allow_html=True)
        
    @st.cache_data(show_spinner=False)
    def get_recent_gdp_forecasts(_self) -> pd.DataFrame:
        """Gets recent forecasts
        for GDP Now"""

        recent_gdp = pd.read_excel(_self.config.vars.gdp_atlanta, sheet_name="TrackingHistory", header=None)
        dates = recent_gdp.iloc[0]
        dates.dropna(inplace=True)
        dates = [str(date)[:10] for date in dates]

        gdp_nowcasts = recent_gdp[recent_gdp[0] == "GDP"].values[0, 2:]
        df_gdp = pd.DataFrame({"Date": dates, "GDP Forecast": gdp_nowcasts})
        cur_fc = recent_gdp.iloc[1, 0][-6:].upper()

        return df_gdp, cur_fc


    @st.cache_data(show_spinner=False)
    def get_data(_self):

        return _self.extract.get_economic_indicators(), _self.extract.get_adamodar_data()
    

    def generate_graphs(self) -> None:
        """Generates dashboard interface"""
        
        self.us_eco_cover()

        c1, c2, c3 = st.columns([4, .5, 3])

        with st.spinner("Carregando os dados..."):
            
            indicator_filter = c1.selectbox(
                "Selecione o indicador econômico", 
                list(self.eco_ind.keys()), 
                index=0 
                )

            year_filter = c3.slider("Selecione uma data inicial", 
                                min_value=2000,
                                max_value=datetime.today().year)
            
            us_econ_data, adamodar_data = self.get_data()
            us_econ_data_choose = us_econ_data[self.eco_ind.get(indicator_filter)]
            us_econ_data_choose = us_econ_data_choose[us_econ_data_choose.index.year >= year_filter]

        c1.markdown(f"""
            <div style="padding-top: 0px; padding-bottom: 0px;">
                <h4 style="margin: 0; color: white">US Economic Indicators - {indicator_filter}</h4>
            </div>
                
            """, unsafe_allow_html=True
        )

        st.line_chart(us_econ_data_choose, color=self.config.base_color)

        with st.spinner("Carregando dados"):
            df_gdp, cur_fc = self.get_recent_gdp_forecasts()

        c1, c2, c3 = st.columns([4, .5, 3])

        c1.markdown(f"""
            <div style="padding-top: 0px; padding-bottom: 0px;">
                <h4 style="margin: 0; color: white">Evolução das previsões para o GDP - {cur_fc}</h4>
            </div>
                
            """, unsafe_allow_html=True
        )
        c1.dataframe(df_gdp, hide_index=True, use_container_width=True)

        c3.markdown(f"""
            <div style="padding-top: 0px; padding-bottom: 0px;">
                <h4 style="margin: 0; color: white">GDP Now - Atlanta FED Forecasts</h4>
            </div>
                
            """, unsafe_allow_html=True
        )

        c3.line_chart(us_econ_data[-1], color=self.config.base_color)

        st.markdown(f"""
                <div style="padding-top: 0px; padding-bottom: 0px;">
                    <h4 style="margin: 0; color: white">Country Default Spreads and Risk Premiums </h4>
                </div>
                    
                """, unsafe_allow_html=True
            )
        st.dataframe(adamodar_data, hide_index=True)
# -*- coding: UTF-8 -*-
"""Import modules"""

from os import path, makedirs, system
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import warnings
import altair as alt
from src.generate import LLMGen


class InfInterest:
    """InfInterest"""

    def __init__(self) -> None:
        """Initializes instance"""

        # import local module
        from src.iface_config import Config
        from src.iface_extract import Extract
        from src.interpolate import Interpolate
        from src.indicators import Indicators

        self.config = Config()
        self.extract = Extract()
        self.interpolate = Interpolate()
        self.chat_bot = LLMGen()
        self.indicators = Indicators()

        self.data_dir = self.config.vars.data_dir
        self.start = datetime(2000, 1, 1)
        self.end = datetime.today()

        warnings.filterwarnings('ignore')

    
    def inf_interest_cover(self):
        """Generates the implied
         inflation and di curve cover"""

        
        st.image(path.join(self.config.vars.img_dir, 
                           self.config.vars.logo_bequest), width=350)
                
        st.markdown("""
                    
                <style>
                [data-baseweb = "tag"] {
                    color: black;
                }
                </style>

                <div style="padding-top: 0px; padding-bottom: 0px;">
                    <h1 style="margin: 0; color: white">Brasil - Inflação Implícita e Curva de Juros</h1>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("""<hr style="height:2px;border:none;color:blue;background-color:#faba19;" /> """,
                        unsafe_allow_html=True)


    @st.cache_data(show_spinner=False)
    def get_data(_self):

        return _self.extract.get_br_implied_inflation()
    

    @st.cache_data(show_spinner=False)
    def get_interest_data(_self, date):

        return _self.interpolate.interpolate(date)


    def generate_graphs(self):
        """Generates Bonds Yields Graphics"""

        self.inf_interest_cover()

        c1, c2, c3 = st.columns([4, 6, 3], vertical_alignment="top")

        col1, col2, col3 = c1.columns([1, 6, .5], vertical_alignment="top")


        input_date = c3.date_input("Digite uma data para saber o juros esperado", 
                                   value = datetime.today() + timedelta(days=30), format="DD/MM/YYYY")

        with st.spinner("Carregando os dados..."):
            
            implied_inflation = self.get_data()
            new_days, target_rates, business_days, interest_rates = self.get_interest_data(input_date)

            df_fut_interest_rate = pd.DataFrame({"Dias Úteis": business_days, 
                                                 "Juros Futuro (DI)": interest_rates,
                                                 "Categoria": "Vencimento Padrão"})
            
            new_interest_dates = pd.DataFrame({"Dias Úteis": new_days, 
                                                 "Juros Futuro (DI)": target_rates,
                                                 "Categoria": f"156, 252 e {new_days[0]} vértices"})
            
            df_final = pd.concat([df_fut_interest_rate, new_interest_dates])


        c1.markdown("""
            <div style="padding-top: 0px; padding-bottom: 0px;">
                    <h4 style="margin: 0; color: white">Inflação Implícita</h4>
            </div>
            """, unsafe_allow_html=True)
        
        c1.dataframe(implied_inflation, hide_index=True, use_container_width=True)
        with c1.popover("Sobre", icon=":material/info:"):
            st.write(self.indicators.all_dict["inf_implicita_br"]["description"])


        c2.markdown(f"""
            <div style="padding-top: 0px; padding-bottom: 0px;">
                    <h4 
                        style="margin: 0; color: white; text-align: center; margin-bottom: 65px;">Curva de Juros mais Recente
                    </h4>
            </div>
            """, unsafe_allow_html=True)
        
        coluna1, coluna2= c2.columns([.5, 7], vertical_alignment="top")
        coluna2.scatter_chart(data=df_final, x="Dias Úteis", y="Juros Futuro (DI)", color="Categoria", 
                         width=500,use_container_width=False)
        
        with c2.popover("Sobre", icon=":material/info:"):
            st.write(self.indicators.all_dict["curva_juros"]["description"])

        c3.markdown(f"""
            <div style="padding-top: 0px; padding-bottom: 0px;">
                    <h4 style="margin: 0; color: white">Juros na data escolhida</h4>
            </div>
            """, unsafe_allow_html=True)

        c3.metric("Valor", f"{target_rates[0]:.2f}%", border=True)



inf_int = InfInterest()
inf_int.generate_graphs()
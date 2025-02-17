# -*- coding: UTF-8 -*-
"""Import modules"""

from os import path, makedirs, system
import pandas as pd
import pandas_datareader.data as pdr
import streamlit as st
from datetime import datetime
import warnings

class MainLayout:
    """MainLayout Interface"""

    def __init__(self) -> None:
        """Initializes instance"""

        # import local module
        from src.iface_config import Config
        from src.dashboard.us_bonds import BondsYields
        from src.dashboard.us_eco import UsEco
        from src.dashboard.us_mkt import UsMkt
        from src.dashboard.sp_mult import SPMult

        self.config = Config()
        self.data_dir = self.config.vars.data_dir
        self.icons_dir = self.config.vars.img_dir
        self.start = datetime(2000, 1, 1)
        self.end = datetime.today()

        warnings.filterwarnings('ignore')

        self.us_bonds = BondsYields()
        self.us_eco = UsEco()
        self.us_mkt = UsMkt()
        self.sp_mult = SPMult()

        st.set_page_config("Financial DashBoard", page_icon="📊", layout="wide", initial_sidebar_state='collapsed')

        if "current_page" not in st.session_state:
            st.session_state["current_page"] = "cover"

    def __repr__(self) -> str:
        """MainLayout Class Basic
        Representation"""

        return f"MainLayout Class, staging dir: {str(self.data_dir)}"
    
    def __str__(self) -> str:
        """MainLayout Class
        Print Representation"""

        return f"MainLayout Class, staging dir: {str(self.data_dir)}"
    

    def set_page(self, page_name):
        """Changes the 
        session state"""
        st.session_state["current_page"] = page_name
        st.rerun()


    def show_cover(self):
        """App cover"""
        if st.session_state["current_page"] != "cover":
            return

        st.image(path.join(self.config.vars.img_dir, 
                           self.config.vars.logo_bequest))

        st.markdown("""
            <div style="padding-top: 0px; padding-bottom: 0px;">
                <h1 style="margin: 0; color: white">DashBoard Financeiro</h1>
            </div>
            """, unsafe_allow_html=True
        )

        st.markdown("""<hr style="height:2px;border:none;color:blue;background-color:#faba19;" /> """,
                    unsafe_allow_html=True)

        st.markdown("""<h2 style="color:white; text-align: center">Selecione um tema</h2>""",
                    unsafe_allow_html=True)

        st.write("#")
        st.write("#")

        self.show_buttons()
        self.side_bar()


    def show_buttons(self):
        """Show theme selector"""
        c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)

        c2.image(path.join(self.config.vars.icons_dir, "cofrinho.png"), width=50)
        if c1.button("Indicadores Econômicos (US)"):
            self.set_page("us_eco_ind")

        c4.image(path.join(self.config.vars.icons_dir, "mercado-de-acoes.png"), width=50)
        if c3.button("Indicadores de Mercado (US)"):
            self.set_page("us_mkt_ind")

        c6.image(path.join(self.config.vars.icons_dir, "etiquetas-de-preco.png"), width=50)
        if c5.button("Múltiplos de Mercado (S&P 500)"):
            self.set_page("sp_mult")

        c8.image(path.join(self.config.vars.icons_dir, "politica.png"), width=50)
        if c7.button("U.S Treasuries Yields"):
            self.set_page("us_bonds")

        st.write("#")
        st.write("#")

        c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)

        c2.image(path.join(self.config.vars.icons_dir, "mercados-emergentes.png"), width=50)
        if c1.button("Indicadores de Mercados Emergentes"):
            self.set_page("em_mkt")

        c4.image(path.join(self.config.vars.icons_dir, "commodities.png"), width=50)
        if c3.button("Commodities Global"):
            self.set_page("comm")

        c6.image(path.join(self.config.vars.icons_dir, "europa.png"), width=50)
        if c5.button("Global ex US"):
            self.set_page("global_ex_us")

        c8.image(path.join(self.config.vars.icons_dir, "inflacao.png"), width=50)
        if c7.button("Inflação Implícita e Juros (BR)"):
            self.set_page("inf_imp_juros")

    
    def side_bar(self):
        """Make a sidebar menu"""

        with st.sidebar:

            st.image(path.join(self.config.vars.img_dir, 
                           self.config.vars.logo_bequest), width=250)
            
            st.write("#")
            
            if st.button("Indicadores Econômicos (US)", key="us_eco_sidebar_button"):
                self.set_page("us_eco_ind")

            if st.button("Indicadores de Mercado (US)", key="us_mkt_sidebar_button"):
                self.set_page("us_mkt_ind")

            if st.button("Múltiplos de Mercado (S&P 500)", key="sp_mult_sidebar_button"):
                self.set_page("sp_mult")

            if st.button("U.S Treasuries Yields", key="us_bonds_sidebar_button"):
                self.set_page("us_bonds")

            if st.button("Indicadores de Mercados Emergentes", key="em_mkt_sidebar_button"):
                self.set_page("em_mkt")

            if st.button("Commodities Global", key="comm_sidebar_button"):
                self.set_page("comm")

            if st.button("Global ex US", key="geus_sidebar_button"):
                self.set_page("global_ex_us")

            if st.button("Inflação Implícita e Juros (BR)", key="inf_sidebar_button"):
                self.set_page("inf_imp_juros")


    def render_page(self):
        """Renders current page"""
        if st.session_state["current_page"] == "cover":
            self.show_cover()
        elif st.session_state["current_page"] == "us_bonds":
            self.us_bonds.generate_graphs()
            self.side_bar()
        elif st.session_state["current_page"] == "us_eco_ind":
            self.us_eco.generate_graphs()
            self.side_bar()
        elif st.session_state["current_page"] == "us_mkt_ind":
            self.us_mkt.generate_graphs()
            self.side_bar()
        elif st.session_state["current_page"] == "sp_mult":
            self.sp_mult.generate_graphs()
            self.side_bar()
        elif st.session_state["current_page"] == "em_mkt":
            st.write("🌍 Indicadores de Mercados Emergentes")
        elif st.session_state["current_page"] == "comm":
            st.write("🌾 Commodities Global")
        elif st.session_state["current_page"] == "global_ex_us":
            st.write("🌏 Global ex US")
        elif st.session_state["current_page"] == "inf_imp_juros":
            st.write("📉 Inflação Implícita e Juros no Brasil")

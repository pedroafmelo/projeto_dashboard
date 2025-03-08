# -*- coding: UTF-8 -*-
"""Import modules"""

from os import path
import streamlit as st
from datetime import datetime
import warnings
from PIL import Image

class MainLayout:
    """MainLayout Interface"""

    def __init__(self) -> None:
        """Initializes instance"""

        # import local modules
        from src.iface_config import Config

        self.config = Config()
        # self.layout = LayoutUtils()
        self.data_dir = self.config.vars.data_dir
        self.icons_dir = self.config.vars.img_dir
        self.start = datetime(2000, 1, 1)
        self.end = datetime.today()

        warnings.filterwarnings('ignore')
        Image.MAX_IMAGE_PIXELS = None


    def __repr__(self) -> str:
        """MainLayout Class Basic
        Representation"""

        return f"MainLayout Class, staging dir: {str(self.data_dir)}"
    
    def __str__(self) -> str:
        """MainLayout Class
        Print Representation"""

        return f"MainLayout Class, staging dir: {str(self.data_dir)}"


    def render_page(self):
        """Renders current page"""

        with st.sidebar:
            
            st.logo(path.join(self.config.vars.img_dir, 
                            self.config.vars.icone_bequest), size="medium")
            st.write("#")

        cover = st.Page("app_pages/cover.py", title="Home", icon=":material/home:")
        us_macro = st.Page("app_pages/usa/macro.py", title="Indicadores Macro", icon=":material/account_balance:", default=True)
        us_market = st.Page("app_pages/usa/markets.py", title="Indicadores de Mercado", icon=":material/finance_mode:")
        # br_macro = st.Page("app_pages/brasil/macro.py", title="Indicadores Macro", icon=":material/savings:")
        # br_market = st.Page("app_pages/brasil/markets.py", title="Indicadores de Mercado", icon=":material/finance_mode:")
        # em_macro = st.Page("app_pages/em_mkts/macro.py", title="Indicadores Macro", icon=":material/savings:")
        # em_market = st.Page("app_pages/em_mkts/markets.py", title="Indicadores de Mercado", icon=":material/finance_mode:")
        # global_macro = st.Page("app_pages/brasil/macro.py", title="Indicadores Macro", icon=":material/savings:")
        # global_market = st.Page("app_pages/brasil/markets.py", title="Indicadores de Mercado", icon=":material/finance_mode:")
        # comm_min = st.Page("app_pages/commodities/comm_min.py", title="Minérios", icon=":material/oil_barrel:")
        # comm_engy = st.Page("app_pages/commodities/comm_energy.py", title="Energia", icon=":material/oil_barrel:")
        # comm_agric = st.Page("app_pages/commodities/comm_grains.py", title="Agricultura", icon=":material/oil_barrel:")
        # comm_indexes = st.Page("app_pages/commodities/comm_indexes.py", title="Índices", icon=":material/oil_barrel:")
        
        pg = st.navigation(
            {
                "Home": [cover],
                "Estados Unidos": [us_macro, us_market],
                # "Brasil": [br_macro, br_market],
                # "Mercados Emergentes": [em_macro, em_market],
                # "Global Ex US": [global_macro, global_market],
                # "Commodities": [comm_min, comm_engy, comm_agric, comm_indexes]
            }
        )

        if st.session_state["authentication_status"] == True:
            pg.run()

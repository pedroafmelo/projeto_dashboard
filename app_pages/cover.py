# -*- coding: UTF-8 -*-
from os import path
import streamlit as st
from src.iface_config import Config
import warnings



class LayoutUtils:
    """Layout Utils class"""

    def __init__(self):
        """Initializes Instance"""

        self.config = Config()

        warnings.filterwarnings("ignore")


    def set_page(self, page_name):
        """Changes the 
        session state"""
        st.session_state["current_page"] = page_name
        st.rerun()
        

    def show_cover(self, text):
        """App cover"""

        # if st.session_state["current_page"] != "cover":
        #     return
        

        columns = st.columns([3, 5, 2])
        columns[0].image(path.join(self.config.vars.img_dir, 
                            self.config.vars.logo_bequest), width=300)

        columns[2].image(path.join(self.config.vars.img_dir, 
                            self.config.vars.logo_pleno), width=300)

        st.markdown(f"""
                    <h1 style="color:white;">{text}</h1>
                    <hr style="height:2px;border:none;color:blue;background-color:#faba19;" />""",
                    unsafe_allow_html=True)
        
        if st.session_state["current_page"] == "cover":
            self.show_buttons()
        
        self.side_bar()


    def show_buttons(self):
        """Show theme selector"""

        st.markdown("""<h2 style="color:white; text-align: center;">Selecione um Tema</h2""",
            unsafe_allow_html=True)
        
        st.write("#")

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
            st.switch_page("app_pages/usa/sp_mult.py")

        c8.image(path.join(self.config.vars.icons_dir, "politica.png"), width=50)
        if c7.button("U.S Treasuries Yields"):
            self.set_page("us_bonds")
            st.switch_page("app_pages/usa/us_bonds.py")

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
            
            st.logo(path.join(self.config.vars.img_dir, 
                            self.config.vars.icone_bequest), size="medium")
            st.write("#")

lu = LayoutUtils()
st.session_state["current_page"] = "cover"
lu.show_cover("Dashboard Financeiro")
import streamlit as st
from app_pages.usa.subpages.cond_fin import UsFinCond
from app_pages.usa.subpages.spread_credito import UsCredSpread
from app_pages.usa.subpages.us_bonds import BondsYields
from app_pages.usa.subpages.mkt_extras import UsExtras
from app_pages.usa.subpages.sp_mult import SPMult

fincond = UsFinCond()
spread = UsCredSpread()
bonds = BondsYields()
extras = UsExtras()
sp_mult = SPMult()
fincond.markets_cover()

if "selected_tab" not in st.session_state:
    st.session_state.selected_tab = "Condições Financeiras"

if st.session_state.selected_tab not in ["Condições Financeiras", "Spread de Crédito", "Bonds Yields", "Preço", "Extras"]:
    st.session_state.selected_tab = "Condições Financeiras"

tabs = ["Condições Financeiras", "Spread de Crédito", "Bonds Yields", "Preço", "Extras"]
selected_tab = st.radio(" ", tabs, index=0, horizontal=True)

if selected_tab != st.session_state.selected_tab:
    st.session_state.selected_tab = selected_tab
    st.rerun()  

if st.session_state.selected_tab == "Condições Financeiras":
    fincond.generate_graphs()
elif st.session_state.selected_tab == "Spread de Crédito":
    spread.generate_graphs()
elif st.session_state.selected_tab == "Bonds Yields":
    bonds.generate_graphs()
elif st.session_state.selected_tab == "Preço":
    sp_mult.generate_graphs()
elif st.session_state.selected_tab == "Extras":
    extras.generate_graphs()
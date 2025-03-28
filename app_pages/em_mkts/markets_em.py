import streamlit as st
from app_pages.em_mkts.subpages.em_spread_cred import EmCredSpread
from app_pages.em_mkts.subpages.em_mult import EmMult
from app_pages.em_mkts.subpages.mkt_extras import EmExtras

spread = EmCredSpread()
mults = EmMult()
extras = EmExtras()
spread.em_markets_cover()

if "selected_tab" not in st.session_state:
    st.session_state.selected_tab = "Condições Financeiras"

if st.session_state.selected_tab not in ["Spread de Crédito", "Preço", "Extras"]:
    st.session_state.selected_tab = "Condições Financeiras"

tabs = ["Spread de Crédito", "Preço", "Extras"]
selected_tab = st.radio(" ", tabs, index=0, horizontal=True)

if selected_tab != st.session_state.selected_tab:
    st.session_state.selected_tab = selected_tab
    st.rerun()  

elif st.session_state.selected_tab == "Spread de Crédito":
    spread.generate_graphs()
elif st.session_state.selected_tab == "Preço":
    mults.generate_graphs()
elif st.session_state.selected_tab == "Extras":
    extras.generate_graphs()
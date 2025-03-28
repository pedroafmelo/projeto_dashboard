import streamlit as st
from app_pages.commodities.subpages.comm_gold import GoldComm
from app_pages.commodities.subpages.comm_energy import EnergyComm
from app_pages.commodities.subpages.comm_grains import GrainsComm
from app_pages.commodities.subpages.comm_indexes import CommIndexes

gold = GoldComm()
energy = EnergyComm()
grains = GrainsComm()
indexes = CommIndexes()
gold.comms_cover()

if "selected_tab" not in st.session_state:
    st.session_state.selected_tab = "Ouro"
    st.session_state["current_page"] = "commodities"

if st.session_state.selected_tab not in ["Ouro", "Energia", "Grãos", "Índices"]:
    st.session_state.selected_tab = "Ouro"

tabs = ["Ouro", "Energia", "Grãos", "Índices"]
selected_tab = st.radio(" ", tabs, index=3, horizontal=True)

if selected_tab != st.session_state.selected_tab:
    st.session_state.selected_tab = selected_tab
    st.rerun()  

if st.session_state.selected_tab == "Ouro":
    gold.generate_graphs()
elif st.session_state.selected_tab == "Energia":
    energy.generate_graphs()
elif st.session_state.selected_tab == "Grãos":
    grains.generate_graphs()
elif st.session_state.selected_tab == "Índices":
    indexes.generate_graphs()
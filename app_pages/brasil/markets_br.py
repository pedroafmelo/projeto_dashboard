import streamlit as st
from app_pages.brasil.subpages.fluxos_inv import BrFlows
from app_pages.brasil.subpages.ibov_mult import IBOVMult
from app_pages.brasil.subpages.juros_br import CurvaJuros

b3_flows = BrFlows()
juros = CurvaJuros()
ibov_mult = IBOVMult()
b3_flows.markets_cover()

if "selected_tab" not in st.session_state:
    st.session_state.selected_tab = "Condições Financeiras Br"

tabs = ["Fluxos de Investimento - B3", "Preço", "Curvas de Juros"]
if st.session_state.selected_tab not in tabs:
    st.session_state.selected_tab = "Condições Financeiras Br"

selected_tab = st.radio(" ", tabs, index=0, horizontal=True)

if selected_tab != st.session_state.selected_tab:
    st.session_state.selected_tab = selected_tab
    st.rerun()  

if st.session_state.selected_tab == "Fluxos de Investimento - B3":
    b3_flows.generate_graphs()
elif st.session_state.selected_tab == "Preço":
    ibov_mult.generate_graphs()
elif st.session_state.selected_tab == "Curvas de Juros":
    juros.generate_graphs()
import streamlit as st
from app_pages.usa.subpages.activity import UsAct
from app_pages.usa.subpages.inflation import UsInf
from app_pages.usa.subpages.ffrate import UsFFR

act = UsAct()
inf = UsInf()
ffr = UsFFR()
act.us_macro_cover()

if "selected_tab" not in st.session_state:
    st.session_state.selected_tab = "Atividade Econômica"
    st.session_state["current_page"] = "atividade"

if st.session_state.selected_tab not in ["Atividade Econômica", "Inflação", "Federal Funds Rate"]:
    st.session_state.selected_tab = "Atividade Econômica"

tabs = ["Atividade Econômica", "Inflação", "Federal Funds Rate"]
selected_tab = st.radio(" ", tabs, index=tabs.index(st.session_state.selected_tab), horizontal=True)

if selected_tab != st.session_state.selected_tab:
    st.session_state.selected_tab = selected_tab
    st.rerun()  

if st.session_state.selected_tab == "Atividade Econômica":
    act.generate_graphs()
elif st.session_state.selected_tab == "Inflação":
    inf.generate_graphs()
elif st.session_state.selected_tab == "Federal Funds Rate":
    ffr.generate_graphs()
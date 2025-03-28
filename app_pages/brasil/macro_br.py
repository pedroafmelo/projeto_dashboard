import streamlit as st
from app_pages.brasil.subpages.activity import BrAct
from app_pages.brasil.subpages.inflation import BrInf
from app_pages.brasil.subpages.selic import BRSelic
from app_pages.brasil.subpages.focus import BrFocus
act = BrAct()
inf = BrInf()
selic = BRSelic()
focus = BrFocus()
act.br_macro_cover()

if "selected_tab" not in st.session_state:
    st.session_state.selected_tab = "Atividade Econômica"
    st.session_state["current_page"] = "atividade"

if st.session_state.selected_tab not in ["Atividade Econômica", "Inflação", "Selic", "Focus"]:
    st.session_state.selected_tab = "Atividade Econômica"

tabs = ["Atividade Econômica", "Inflação", "Selic", "Focus"]
selected_tab = st.radio(" ", tabs, index=0, horizontal=True)

if selected_tab != st.session_state.selected_tab:
    st.session_state.selected_tab = selected_tab
    st.rerun()  

if st.session_state.selected_tab == "Atividade Econômica":
    act.generate_graphs()
elif st.session_state.selected_tab == "Inflação":
    inf.generate_graphs()
elif st.session_state.selected_tab == "Selic":
    selic.generate_graphs()
elif st.session_state.selected_tab == "Focus":
    focus.generate_graphs()
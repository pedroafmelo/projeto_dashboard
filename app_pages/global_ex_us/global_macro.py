import streamlit as st
from app_pages.global_ex_us.subpages.activity import GlobalAct
from app_pages.global_ex_us.subpages.inflation import GlobalInf
from app_pages.global_ex_us.subpages.juros_global import GlobalInt
from app_pages.global_ex_us.subpages.risco_global import GlobalRisk

act = GlobalAct()
inf = GlobalInf()
juros = GlobalInt()
risk = GlobalRisk()
act.em_macro_cover()

if "selected_tab" not in st.session_state:
    st.session_state.selected_tab = "Atividade Econômica"
    st.session_state["current_page"] = "atividade"

if st.session_state.selected_tab not in ["Atividade Econômica", "Inflação", "Taxas de Juros", "Risco"]:
    st.session_state.selected_tab = "Atividade Econômica"

tabs = ["Atividade Econômica", "Inflação", "Taxas de Juros", "Risco"]
selected_tab = st.radio(" ", tabs, index=0, horizontal=True)

if selected_tab != st.session_state.selected_tab:
    st.session_state.selected_tab = selected_tab
    st.rerun()  

if st.session_state.selected_tab == "Atividade Econômica":
    act.generate_graphs()
elif st.session_state.selected_tab == "Inflação":
    inf.generate_graphs()
elif st.session_state.selected_tab == "Taxas de Juros":
    juros.generate_graphs()
elif st.session_state.selected_tab == "Risco":
    risk.generate_graphs()
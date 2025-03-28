import streamlit as st
from app_pages.global_ex_us.subpages.global_mult import GlobalMult

global_mult = GlobalMult()

global_mult.global_markets_cover()
global_mult.generate_graphs()

from src.dashboard.main_layout import MainLayout
import streamlit_authenticator as stauth
import streamlit as st
import pickle
from pathlib import Path
from src.iface_config import Config
from authentications import Authentication

if __name__ == "__main__":

    auth = Authentication()
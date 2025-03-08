import pickle
import yaml
from yaml import SafeLoader
from pathlib import Path
from os import path
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import (CredentialsError,
                                               ResetError)
from app_pages.main import MainLayout
from src.iface_config import Config
from PIL import Image


class Authentication:
    """User Authentication class"""

    def __init__(self):
        """Applies login system"""

        self.config = Config()
        Image.MAX_IMAGE_PIXELS = None

        yaml_file = Path(__file__).parent / "credentials.yaml"

        with yaml_file.open("r") as file:
            config = yaml.load(file, SafeLoader)

        stauth.Hasher.hash_passwords(config["credentials"])

        if "authentication_status" not in st.session_state:
            st.session_state["authentication_status"] = None

        if "current_page" not in st.session_state:
            st.session_state["current_page"] = "cover"

        if st.session_state["current_page"] == "cover" and st.session_state["authentication_status"] == True:
            sidebar_state = "expanded"
            
        else :
            
            sidebar_state = "collapsed"


        st.set_page_config(
            page_title="Financial DashBoard",
            page_icon=path.join(self.config.vars.img_dir,
                                self.config.vars.icone_bequest),
            layout="wide",
            initial_sidebar_state=sidebar_state,
        )

        st.markdown(
            """
                <style>
                    .block-container {
                            padding-top: 1rem;
                            padding-bottom: 0rem;
                            padding-left: 5rem;
                            padding-right: 5rem;
                        }
                </style>
                """,
            unsafe_allow_html=True,
        )

        st.html("/Users/pedroafmelo/Documents/pleno_finance/projeto_dashboard/app_pages/styles.html")


        with yaml_file.open("r") as file:
             config = yaml.load(file, SafeLoader)

        authenticator = stauth.Authenticate(
            config["credentials"],
            config["cookie"]["name"],
            config["cookie"]["key"],
            config["cookie"]["expiry_days"]
        )

        

        col1, col2, col3 = st.columns([1, 3, 1])
        c1, c2, c3 = col2.columns([.7,3,1])

        with c2:
            authenticator.login()


        if st.session_state["authentication_status"] == True:
            
            ml = MainLayout()
            ml.render_page()

            with st.sidebar:
                
                st.write("#")
                authenticator.logout("Logout")
                
                try:
                    if authenticator.reset_password(st.session_state["username"], 
                                                    fields={"Current password": "Senha Atual",
                                                            "New password": "Nova Senha",
                                                            "Repeat password": "Repetir Senha"},):
                        st.success("Senha alterada com sucesso")

                        st.write(config)

                        with yaml_file.open("w") as file:
                            yaml.dump(config, file, sort_keys=False, 
                                    default_flow_style=False)
                    
                except ResetError:
                     st.error("A nova senha deve conter A-Z, a-z, 0-9, [@$!%*?&], e no mínimo 8 e máximo 20 caracteres!")
                     
                except CredentialsError as e:
                    st.error("As credenciais providas não estão corretas")       

        elif st.session_state["authentication_status"] == False:
            st.markdown(
                """
            <style>
                [data-testid="collapsedControl"] {
                    display: none
                }
            </style>
            """,
                unsafe_allow_html=True,
            )
            c2.error("Usuário/Senha incorreto(s)")

        elif st.session_state['authentication_status'] is None:

            st.logo(path.join(self.config.vars.img_dir, 
                           self.config.vars.logo_bequest), size="large")

            st.markdown(
                """
            <style>
                [data-testid="collapsedControl"] {
                    display: none
                }
            </style>
            """,
                unsafe_allow_html=True,
            )
            c2.warning('Por favor, entre com login e senha') 


        with yaml_file.open("w") as file:
            yaml.dump(config, file, default_flow_style=False)
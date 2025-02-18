import pickle
import yaml
from yaml import SafeLoader
from pathlib import Path
from os import path
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import (CredentialsError,
                                               ResetError)
from src.dashboard.main_layout import MainLayout
from src.iface_config import Config


class Authentication:
    """User Authentication class"""

    def __init__(self):
        """Applies login system"""

        self.config = Config()

        yaml_file = Path(__file__).parent / "credentials.yaml"

        with yaml_file.open("r") as file:
            config = yaml.load(file, SafeLoader)

        stauth.Hasher.hash_passwords(config["credentials"])

        if "current_page" not in st.session_state:
            st.session_state["current_page"] = "cover"

        sidebar_state = "expanded" if st.session_state["current_page"] == "cover" else "collapsed"

        st.set_page_config(
            page_title="Financial DashBoard",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state=sidebar_state,
        )

        authenticator = stauth.Authenticate(
            config["credentials"],
            config["cookie"]["name"],
            config["cookie"]["key"],
            config["cookie"]["expiry_days"]
            )
        
        if "authentication_status" not in st.session_state:
            st.session_state["authentication_status"] = None

        if st.session_state["authentication_status"] == None:
            st.image(path.join(self.config.vars.img_dir, 
                           self.config.vars.logo_bequest))

            st.markdown("""<hr style="height:2px;border:none;color:blue;background-color:#faba19;" /> """,
                    unsafe_allow_html=True)
            st.write("#")

        col1, col2, col3 = st.columns([1, 3, 1])

        with col2:
            authenticator.login()

        if st.session_state["authentication_status"]:
            
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
            col2.error("Usuário/Senha incorreto(s)")

        elif st.session_state['authentication_status'] is None:

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
            col2.warning('Please enter your username and password') 

        with yaml_file.open("w") as file:
            yaml.dump(config, file, default_flow_style=False)
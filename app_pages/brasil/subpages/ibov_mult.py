# -*- coding: UTF-8 -*-
"""Import modules"""

from os import path, makedirs, system
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import warnings
import altair as alt
import requests
import pandas_datareader.data as pdr
from streamlit_echarts import st_echarts
import numpy as np
import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains


class IBOVMult:
    """Ibovespa Multiples"""

    def __init__(self) -> None:
        """Initializes instance"""

        # import local module
        from src.iface_config import Config
        from src.iface_extract import Extract
        from src.indicators import Indicators
        from app_pages.utils import Utils

        self.config = Config()
        self.extract = Extract()
        self.indicators = Indicators()
        self.utils = Utils()

        self.data_dir = self.config.vars.data_dir
        self.start = datetime(2000, 1, 1)
        self.end = datetime.today()

        self.ind = self.indicators.get_theme_dict("br_mkt_preco")
        self.ind_ids = self.indicators.get_ids_list("br_mkt_preco")

        self.ibov_mult= dict(zip(list(self.ind.keys()), 
                               list(range(1))))
        
        warnings.filterwarnings('ignore')

    
    def scrap_ibov_pl(self):

        try:

            chrome_options = webdriver.ChromeOptions()
            # chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                                    options=chrome_options)
            driver.get(self.config.vars.pl_ibov)
            driver.maximize_window()
            driver.implicitly_wait(9)

            graph_elem = driver.find_element("xpath", '//*[@id="tab"]/div/div[3]/div')
            driver.execute_script("arguments[0].scrollIntoView();", graph_elem)
            time.sleep(7)

            action = ActionChains(driver)

            x_inicial = 0
            x_final = 1052
            y_offset=10

            graph = driver.find_element(By.XPATH, '//*[@id="grafHistoricoPlBovespa"]')

            action.move_to_element_with_offset(graph, x_inicial, y_offset).perform()

            list_pls = []
            list_data = []
            local_valor = '//*[@id="grafHistoricoPlBovespa"]/div[2]/b[2]'
            local_data = '//*[@id="grafHistoricoPlBovespa"]/div[2]/b[1]'
            action.move_by_offset(-505, 0).perform()

            for i in range(x_inicial, x_final - x_inicial):
                action.move_by_offset(1, 0).perform()
                time.sleep(0.01)
                try:
                    pl_element = driver.find_element("xpath", local_valor)
                    list_pls.append(pl_element.text)
                    date_elem = driver.find_element("xpath", local_data)
                    list_data.append(date_elem.text)
                except Exception as error:
                    raise OSError(error) from error
                
            driver.quit()  
        
        except Exception as error:
            raise OSError(error) from error
        
        df_pl_ibov = pd.DataFrame({"Data": list_data, "PL": list_pls})
        df_pl_ibov.to_excel("pl_ibov.xlsx", index=False)

        return "Extraction Done"

    
    @st.cache_data(show_spinner=False)
    def get_ibov_multiples(_self) -> pd.DataFrame:
        """Reads the IBOV multiples sheet"""

        try:
            dados = pd.read_excel(path.join(
                _self.config.vars.data_dir,
                "pl_ibov.xlsx"
            ))
            dados = dados.assign(
                Data = lambda x: pd.to_datetime(x["Data"], format="%d/%m/%Y"),
                PL = lambda x: x["PL"].str.replace(",", ".").astype(float)
            )
            dados.set_index("Data", inplace=True)

        except Exception as error:
            raise OSError(error) from error
        
        return dados


    def generate_graphs(self):
        """Generates dashboard interface"""

        c1, c2, c3 = st.columns([2, .5, 1])
        coluna1, coluna2, coluna3 = c1.columns([4,1,4], vertical_alignment="center")

        with st.spinner("Carregando os dados..."):
            
            pl_ibov = self.get_ibov_multiples()
        
        c1, c2, c3 = st.columns([6, .5, 2], vertical_alignment="center")
        
        options = self.utils.echart_dict(pl_ibov, title="P/L Ibovespa", mean=True)
        formatter = ""
        
        with c1.container():
            st.html("<span class='column_graph'></span>")
            col,_ = st.columns([10,.05])
            with col:
                st_echarts(options, height="500px", theme="dark")

        current_value = round(pl_ibov.iloc[-1].values[0], 3)
        lowest_value = round(pl_ibov.min().values[0], 3)
        highest_value = round(pl_ibov.max().values[0], 3)
        
        with c3:
            co1, co2, co3 = st.columns([1, 3, 1])
            st.html("<span class='indicators'></span>")
            co2.metric("Valor Atual", f"{current_value}{formatter}")
            co2.metric("Maior Valor", f"{highest_value}{formatter}")
            co2.metric("Menor Valor", f"{lowest_value}{formatter}")

        with c1.popover("Sobre", icon=":material/info:"):
                st.markdown(self.ind["Preço sobre Lucro (P/L) do Ibovespa"]["description"], unsafe_allow_html=True)
# -*- coding: UTF-8 -*-
"""Import modules"""

from os import path, makedirs, system
import pandas as pd
import pandas_datareader.data as pdr
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import yfinance as yf
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import warnings
from fredapi import Fred

class Extract:
    """Extract Interface"""

    def __init__(self) -> None:
        """Initializes instance"""

        # import local module
        from iface_config import Config

        self.config = Config()
        self.data_dir = self.config.vars.data_dir
        self.start = datetime(2000, 1, 1)
        self.end = datetime.today()

        self.fred = Fred(api_key=self.config.vars.FRED_API_KEY)

        warnings.filterwarnings('ignore')

    def __repr__(self) -> str:
        """Extract Class Basic
        Representation"""

        return f"Extract Class, staging dir: {str(self.data_dir)}"
    
    def __str__(self) -> str:
        """Extract Class
        Print Representation"""

        return f"Extract Class, staging dir: {str(self.data_dir)}"
    

    def get_bonds_yields(self):
        """Downloads the US Gov
          Bonds Yields"""
        
        bonds_list = [
            self.config.vars.t_2_y, 
            self.config.vars.t_5_y,
            self.config.vars.t_10_y,
            self.config.vars.t_20_y,
            self.config.vars.t_30_y
            ]
        
        makedirs(path.join(self.data_dir,
                           "us_gov_bonds"), exist_ok=True)
        
        for yield_ in bonds_list:
            
            try:
                yield_series = pdr.DataReader(yield_, "fred", self.start, self.end)
                yield_series.to_csv(path.join(self.data_dir, 
                                            "us_gov_bonds",
                                            f"{yield_}.csv.gz"), compression="gzip")
            except Exception as error:
                raise OSError(error) from error

        return "Extraction Done"
    

    def get_sp_multiples(self) -> str:
        """Scraps the S&P500
        multiples"""

        earnings_url = self.config.vars.mult_base_url
        mults_list =[
            self.config.vars.sp_earnings_yields,
            self.config.vars.sp_pe,
            self.config.vars.sp_pb
        ]
        mults_dict = {
            self.config.vars.sp_earnings_yields: [],
            self.config.vars.sp_pe: [],
            self.config.vars.sp_pb: []
        }

        makedirs(path.join(self.data_dir,
                           "sp_multiples"), exist_ok=True)

        for mult in mults_list:

            try:
                response = requests.get(f"{earnings_url}/{mult}", verify=False)
                if not response.ok:
                    raise FileNotFoundError(f"Unable to request the {mult}")
                
                soup = BeautifulSoup(response.content, "html.parser")
                elems = [elem.text.strip() for elem in soup.find_all("td")]
                mults_dict[mult] = elems

            except Exception as error:
                raise OSError(error) from error

        sp_ey = [round(
            float(elem.strip("†\n")[:-1])/100, 4
            ) for elem 
            in mults_dict[self.config.vars.sp_earnings_yields][::-1] 
            if "%" in elem][:-1]

        sp_pe = [float(elem.strip("†\n")[:-1]) for elem 
            in mults_dict[self.config.vars.sp_pe][::-1]
            if "." in elem][:-1]
        
        sp_pb = [float(elem.strip("†\n")) for elem 
                 in mults_dict[self.config.vars.sp_pb][::-1] if "." in elem][:-1]
        
        index_date_ey_pe = [elem for elem 
            in mults_dict[self.config.vars.sp_pe][::-1]
            if "." not in elem][:-1]
        
        index_date_pb = [elem for elem 
                 in mults_dict[self.config.vars.sp_pb][::-1] if "," in elem][:-1]

        df_ey_pe = pd.DataFrame({
            "Date": index_date_ey_pe, 
            "earning_yields": sp_ey,
            "price_earnings": sp_pe,
        })

        df_pb = pd.DataFrame({
            "Date": index_date_pb, 
            "earning_yields": sp_pb,
        })

        df_ey_pe.to_csv(path.join(self.data_dir,
                                  "sp_multiples",
                                  "sp_ey_pe.csv.gz"), compression="gzip")
        
        df_pb.to_csv(path.join(self.data_dir,
                                  "sp_multiples",
                                  "sp_pb.csv.gz"), compression="gzip")
        
        return "Extraction done"
    

    def get_economic_indicators(self) -> str:
        """Download USA Economic
          Indicators"""

        indicators_list = [
            self.config.vars.ind_production, 
            self.config.vars.cpi_urban,
            self.config.vars.pce,
            self.config.vars.implied_inflation,
            ]
        
        makedirs(path.join(self.data_dir,
                           "economic_indicators"), exist_ok=True)
        
        for indicator in indicators_list:
            
            try:
                yield_series = pdr.DataReader(indicator, "fred", self.start, self.end)
                yield_series.to_csv(path.join(self.data_dir, 
                                            "economic_indicators",
                                            f"{indicator}.csv.gz"), compression="gzip")
            except Exception as error:
                raise OSError(error) from error

        return "Extraction Done"
    

    def get_market_indicators(self) -> str:
        """Download USA Market
          Indicators"""

        indicators_list = [
            self.config.vars.liquidity_spread, 
            self.config.vars.ice_bofa_hy_spread,
            self.config.vars.ice_bofa_cred_spread,
            self.config.vars.chicago_fci,
            self.config.vars.leverage_subindex,
            self.config.vars.risk_subindex,
            self.config.vars.non_financial_leverage,
            ]
        
        makedirs(path.join(self.data_dir,
                           "market_indicators"), exist_ok=True)
        
        for indicator in indicators_list:
            try:
                indicator_series = self.fred.get_series(indicator,
                                                        observation_start=self.start, 
                                                        observation_end=self.end)
                indicator_series.to_csv(path.join(self.data_dir, 
                                            "market_indicators",
                                            f"{indicator}.csv.gz"), compression="gzip")
            except Exception as error:
                raise OSError(error) from error
            
        try:
            dxy = yf.download(self.config.vars.dxy, start=self.start, end=self.end)["Close"]
            dxy.to_csv(path.join(self.data_dir, 
                                            "market_indicators",
                                            f"{self.config.vars.dxy}.csv.gz"), compression="gzip")
            
        except Exception as error:
                raise OSError(error) from error
            
        try:
            asset_series = pdr.DataReader(self.config.vars.equity_rf, "famafrench", self.start, self.end)[0]
            asset_series.to_csv(path.join(self.data_dir, 
                                            "market_indicators",
                                            f"{self.config.vars.equity_rf}.csv.gz"), compression="gzip")
        except Exception as error:
                raise OSError(error) from error

        return "Extraction Done"
    

    def get_commodities(self) -> str:
        """Download Commodities"""

        commodities_list = [
            self.config.vars.gsci,
            self.config.vars.oil_gas,
            self.config.vars.agriculture_index
        ]

        makedirs(path.join(
            self.data_dir,"commodities"),
            exist_ok=True)

        for comm in commodities_list:
            try:
                comm_series = yf.download(comm, start=self.start, end=self.end)["Adj Close"]
                comm_series.to_csv(path.join(self.data_dir, 
                                            "commodities",
                                            f"{comm}.csv.gz"), compression="gzip")
            except Exception as error:
                raise OSError(error) from error
            
        return "Extraction Done"
            
        
    def get_emerging_data(self) -> str:
        """Download Emerging
        Markets Data"""

        emerging_indicators = [
            self.config.vars.ice_bofa_hy_em_spread,
            self.config.vars.ice_bofa_cred_em_spread,
            self.config.vars.em_etfs_vol,
            self.config.vars.em_non_fin_ice_bofa,
            self.config.vars.asia_em_bofa,
            self.config.vars.latin_em_bofa,
            self.config.vars.euro_em_bofa
        ]

        makedirs(path.join(self.data_dir,
                           "em_indicators"), exist_ok=True)
        
        for em_ind in emerging_indicators:
            try:
                indicator_series = self.fred.get_series(em_ind,
                                                        observation_start=self.start, 
                                                        observation_end=self.end)
                indicator_series.to_csv(path.join(self.data_dir, 
                                            "em_indicators",
                                            f"{em_ind}.csv.gz"), compression="gzip")
            except Exception as error:
                raise OSError(error) from error
            
        try:
            dxy = yf.download(self.config.vars.emb, start=self.start, end=self.end)["Close"]
            dxy.to_csv(path.join(self.data_dir, 
                                            "em_indicators",
                                            f"{self.config.vars.dxy}.csv.gz"), compression="gzip")
        except Exception as error:
                raise OSError(error) from error

        return "Extraction Done"
    

    def get_global_exus_data(self) -> str:
        """Download Global 
        ex US data"""

        makedirs(path.join(self.data_dir, 
                           "global_ex_us"), exist_ok=True)

        try:
            spdw = yf.download(self.config.vars.global_ex_us_etf, 
                        start=self.start, end=self.end)["Adj Close"]
            spdw.to_csv(path.join(
                    self.data_dir,
                    "global_ex_us",
                    f"{self.config.vars.global_ex_us_etf}.csv.gz"
            ), compression="gzip")

        except Exception as error:
            raise OSError(error) from error
        

        return "Extraction Done"
    

    def get_br_implied_inflation(self) -> str:
        """Scrap Implied Inflation
        data for specific vertices"""

        makedirs(path.join(
            self.data_dir,
            "em_indicators"
        ), exist_ok=True)

        url = self.config.vars.inf_implicita_br

        try:
            response = requests.get(url)
            if not response.ok:
                raise FileNotFoundError(f"Unable to request the AMBIMA web site")
            soup = BeautifulSoup(response.content, "html.parser")

            lista_elems = [elem.text for elem in soup.find_all("div", id="ETTJs")]
            lista_elems = [elem.replace("\n", " ").replace("\t", " ") for elem in lista_elems]
            lista_elems = lista_elems[0].split(" ")
            lista_elems = [elem for elem in lista_elems if elem not in [" ", ""]]
            lista_elems = lista_elems[lista_elems.index("Implícita") + 1:lista_elems.index("2.394") + 4]

            lista_vertices = [int(lista_elems[i].replace(".", "")) for i in range(0, len(lista_elems) - 2, 4)]
            lista_eetj_ntnb = [float(lista_elems[i].replace(",", ".")) for i in range(1, len(lista_elems) - 1, 4)]
            lista_eetj_pre = [float(lista_elems[i].replace(",", ".")) for i in range(2, len(lista_elems), 4)]
            lista_inf_implicita = [float(lista_elems[i].replace(",", ".")) for i in range(3, len(lista_elems) + 1, 4)]

        except Exception as error:
            raise OSError(error) from error
        
        df_implicita = pd.DataFrame({"vertice": lista_vertices,
                                     "ETTJ_PRE": lista_eetj_pre,
                                     "ETTJ_NTNB": lista_eetj_ntnb,
                                     "Inflacao_Implicita": lista_inf_implicita})
        
        df_implicita.to_csv(path.join(
            self.data_dir,
            "em_indicators",
            "inf_implicita_br.csv.gz"
        ), compression="gzip")

        return "Extraction Done"


e = Extract()

print(e.get_commodities()) 
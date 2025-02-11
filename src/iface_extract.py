# -*- coding: UTF-8 -*-
"""Import modules"""

from os import path, makedirs
import pandas as pd
import pandas_datareader.data as pdr
from datetime import datetime
from bs4 import BeautifulSoup
import requests
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
import warnings

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
    

    def get_assets_returns(self) -> str:
        """Downloads the asset
         classes proxys dfs"""
        
        assets_returns_list = {
            self.config.vars.equity: "famafrench",
            self.config.vars.credits: "fred",
            self.config.vars.high_yields: "fred"
        }

        makedirs(path.join(self.data_dir,
                           "asset_classes"), exist_ok=True)

        for asset_class, source in assets_returns_list.items():
            
            try:
                asset_series = pdr.DataReader(asset_class, source, self.start, self.end)
                if len(asset_series) == 3:
                    asset_series = asset_series[0]
                asset_series.to_csv(path.join(self.data_dir, 
                                            "asset_classes",
                                            f"{asset_class}.csv.gz"), compression="gzip")
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
            self.config.vars.ice_bofa_spread,
            self.config.vars.chicago_fci,
            self.config.vars.leverage_subindex,
            self.config.vars.risk_subindex,
            self.config.vars.non_financial_leverage,
            ]
        
        makedirs(path.join(self.data_dir,
                           "market_indicators"), exist_ok=True)
        
        for indicator in indicators_list:
            
            try:
                yield_series = pdr.DataReader(indicator, "fred", self.start, self.end)
                yield_series.to_csv(path.join(self.data_dir, 
                                            "economic_indicators",
                                            f"{indicator}.csv.gz"), compression="gzip")
            except Exception as error:
                raise OSError(error) from error

        return "Extraction Done"
    
e = Extract()

print(e.get_economic_indicators()) 
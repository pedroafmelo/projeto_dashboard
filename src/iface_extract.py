# -*- coding: UTF-8 -*-
"""Import modules"""

from os import path, makedirs, system
import pandas as pd
import pandas_datareader.data as pdr
from datetime import datetime
from bs4 import BeautifulSoup
import requests
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries

import warnings
from fredapi import Fred

class Extract:
    """Extract Interface"""

    def __init__(self) -> None:
        """Initializes instance"""

        # import local module
        from src.iface_config import Config
        from src.indicators import Indicators

        self.config = Config()
        self.indicators = Indicators()
        self.data_dir = self.config.vars.data_dir
        self.start = datetime(2000, 1, 1)
        self.end = datetime.today()

        self.fred = Fred(api_key=self.config.vars.FRED_API_KEY)
        self.av_tseries = TimeSeries(key=self.config.vars.AV_API_KEY, 
                             output_format="pandas")

        warnings.filterwarnings('ignore')

    def __repr__(self) -> str:
        """Extract Class Basic
        Representation"""

        return f"Extract Class, staging dir: {str(self.data_dir)}"
    
    def __str__(self) -> str:
        """Extract Class
        Print Representation"""

        return f"Extract Class, staging dir: {str(self.data_dir)}"
    
    


    


    

    
    

            
        
    def get_emerging_data(self) -> pd.DataFrame | list:
        """Download Emerging
        Markets Data"""

        ind_list = []
        for ind in self.indicators.get_ids_list("emerging_markets"):
            try:
                indicator_series = self.fred.get_series(ind,
                                                        observation_start=self.start, 
                                                        observation_end=self.end)
                indicator_series = indicator_series.to_frame(name=ind)
                indicator_series.index.name = "Date"
                ind_list.append(indicator_series)
            except Exception as error:
                raise OSError(error) from error
            
        df_final = pd.concat(ind_list, axis=1)
            
        return df_final


    def get_emb_series(self) -> pd.DataFrame:
        """Downloads EMB etf
        series"""

        emb = None
        
        try:
            emb = yf.download(self.indicators.get_ids_list("emb"), start=self.start, end=self.end)["Close"]
        except Exception as error:
            raise OSError(error) from error
        
        if emb is None or emb.empty:
            emb, metadata = self.av_tseries.get_daily(self.config.vars.emb,
                                             outputsize="full")
            emb.sort_index(inplace=True)
            emb = emb["4. close"]

        return emb
    

    def get_vxeem(self) -> pd.DataFrame:
        """Downloads VXEEMCLS index
        series"""
        
        try:
            for ind in self.indicators.get_ids_list("vxeem"):
                vxeem = self.fred.get_series(ind,
                                        observation_start=self.start, 
                                        observation_end=self.end)
                vxeem = vxeem.to_frame()
                vxeem.dropna(inplace=True)
                vxeem.index.name="Date"

        except Exception as error:
                raise OSError(error) from error

        return vxeem
    

    def get_global_exus_data(self) -> pd.DataFrame:
        """Download Global 
        ex US data"""

        try:
            spdw = yf.download(self.indicators.get_ids_list("global_ex_us"), 
                        start=self.start, end=self.end)["Close"]

        except Exception as error:
            raise OSError(error) from error
        
        if len(spdw) == 0:
            spdw, metadata = self.av_tseries.get_daily("SPDW", outputsize="full")
            spdw.sort_index(inplace=True)
            spdw = spdw["4. close"]

        return spdw
    
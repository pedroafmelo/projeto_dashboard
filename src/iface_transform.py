# -*- coding: UTF-8 -*-
"""Import modules"""

import os
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

class Transform:
    """Transform Interface"""

    def __init__(self) -> None:
        """Initializes instance"""

        # import local module
        from iface_config import Config
        from iface_extract import Extract

        self.config = Config()
        self.extract = Extract()

        self.data_dir = self.config.vars.data_dir
        self.start = datetime(2000, 1, 1)
        self.end = datetime.today()

        self.fred = Fred(api_key=self.config.vars.FRED_API_KEY)


        warnings.filterwarnings('ignore')

    def __repr__(self) -> str:
        """Transform Class Basic
        Representation"""

        return f"Transform Class, staging dir: {str(self.data_dir)}"
    
    def __str__(self) -> str:
        """Transform Class
        Print Representation"""

        return f"Transform Class, staging dir: {str(self.data_dir)}"
    

            


t = Extract()
print(t.check_files())
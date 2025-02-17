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
# -*- coding: UTF-8 -*-
"""Import modules"""

from os import path, system
import pandas as pd
from datetime import datetime, timedelta
from scipy import interpolate
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import warnings
import holidays

class Interpolate:
    """Interpolate Interface"""

    def __init__(self) -> None:
        """Initializes instance"""

        # import local module
        from src.iface_config import Config

        self.config = Config()
        self.data_dir = self.config.vars.data_dir
        self.start = datetime(2000, 1, 1)
        self.end = datetime.today()

        warnings.filterwarnings('ignore')

    def __repr__(self) -> str:
        """Interpolate Class Basic
        Representation"""

        return f"Interpolate Class, staging dir: {str(self.data_dir)}"

    def __str__(self) -> str:
        """Interpolate Class
        Print Representation"""

        return f"Interpolate Class, staging dir: {str(self.data_dir)}"
    
    @staticmethod
    def ajustar_para_dia_util(data_hora, pais='BR'):
        feriados = holidays.country_holidays(pais)
        
        data_hora -= timedelta(days=1)
        
        while data_hora.weekday() in [5, 6] or data_hora.date() in feriados:
            data_hora -= timedelta(days=1)
    
        return data_hora.replace(hour=11, minute=0, second=0)


    def get_di_table(self, mercadoria: str = "DI1") -> pd.DataFrame:
        """Get the CDI table 
        for given date"""

        date = self.ajustar_para_dia_util(datetime.today())
        date = datetime.strftime(date, format=r"%d/%m/%Y")
        url = self.config.vars.di_future.replace(r"{data_di}", date).replace(r"{mercadoria}", mercadoria)
        chrome_options = Options()
        chrome_options.add_argument("--headless")  
        chrome_options.add_argument("--disable-gpu")  
        chrome_options.add_argument("--no-sandbox")

        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.get(url)
            driver.implicitly_wait(5)

            local_table = "/html/body/div/div[2]/form[1]/table[3]/tbody/tr[3]/td[3]/table"
            local_index = "/html/body/div/div[2]/form[1]/table[3]/tbody/tr[3]/td[1]/table"

            element_table = driver.find_element("xpath", local_table)
            element_index = driver.find_element("xpath", local_index)

            html_table = element_table.get_attribute("outerHTML")
            html_index = element_index.get_attribute("outerHTML")

            table = pd.read_html(html_table)[0]
            index = pd.read_html(html_index)[0]

            driver.quit()

        except Exception as error:
            raise OSError(error) from error

        table.columns = table.loc[0]
        table = table["ÚLT. PREÇO"]
        table.drop(0, axis=0, inplace=True)

        index.columns = index.loc[0]
        index.drop(0, axis=0, inplace=True)

        table.index = index["VENCTO"]
        table = table.astype(float)
        table = table/1000
        table = table[table != 0]

        translator = pd.Series(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                    index = ['F', 'G', 'H', 'J', 'K', 'M', 'N', 
                             'Q', 'U', 'V', 'X', 'Z'])

        dates_list = []

        for index in table.index:
            letter = index[0]
            year = index[1:3]
            month = translator[letter]
            date = datetime.strptime(f"{month}-{year}", "%b-%y")

            dates_list.append(date)

        table.index = dates_list

        return table


    def get_anbima_holidays(self) -> pd.DataFrame:
        """Gets ANBIMA National
        Holidays"""

        try:

            data_anbima = pd.read_excel(self.config.vars.ambima_holidays)[:-9]
            data_anbima["Data"] = pd.to_datetime(data_anbima["Data"], format=r"%Y-%m-%d")
            data_anbima = data_anbima[data_anbima["Data"] >= self.end]["Data"].to_list()

        except Exception as error:
            raise OSError(error) from error

        return data_anbima


    def interpolate(self, date):
        """Interpolate DI Interest Rate
        Return In date Rate"""


        holidays = self.get_anbima_holidays()
        di_table = self.get_di_table()
        bus_days_list = []

        for day in di_table.index:
            try:
                bus_days = len(
                    pd.date_range(
                        self.end,
                        day,
                        freq=pd.tseries.offsets.CustomBusinessDay(holidays=holidays),
                    )
                )
                bus_days_list.append(bus_days)

            except Exception as error:
                raise OSError(error) from error

        rates = list(di_table.values)

        try:
            forward_bus_days = len(
                pd.date_range(
                    self.end,
                    date, 
                    freq=pd.tseries.offsets.CustomBusinessDay(holidays=holidays)
                    )
                )
            cubic = interpolate.interp1d(bus_days_list, rates, kind="cubic")
            new_days = [forward_bus_days, 126, 252]

        except Exception as error:
            raise OSError(error) from error

        cubic_rates = list(cubic(new_days))

        return new_days, cubic_rates, bus_days_list, rates
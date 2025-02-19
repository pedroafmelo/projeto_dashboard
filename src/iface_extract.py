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

        self.config = Config()
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
    

    def get_bonds_yields(self) -> pd.DataFrame | list:
        """Downloads the US Gov
          Bonds Yields"""
        
        try:
            yield_series = pdr.DataReader(self.config.vars.us_bonds_yields, "fred", self.start, self.end)
        except Exception as error:
            raise OSError(error) from error

        return yield_series
    

    def get_sp_multiples(self) -> pd.DataFrame | tuple:
        """Scraps the S&P500
        multiples"""

        multas_base_url = self.config.vars.mult_base_url
        mults_dict = {mult: [] for mult in self.config.vars.sp_mult}

        for mult in self.config.vars.sp_mult:

            try:
                response = requests.get(f"{multas_base_url}/{mult}", verify=False)
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
            in mults_dict[self.config.vars.sp_mult[0]][::-1] 
            if "%" in elem]

        sp_pe = [float(elem.strip("†\n")[:-1]) for elem 
            in mults_dict[self.config.vars.sp_mult[1]][::-1]
            if "." in elem]
        
        sp_pb = [float(elem.strip("†\n")) for elem 
                 in mults_dict[self.config.vars.sp_mult[2]][::-1] if "." in elem]
        
        index_date_ey_pe = [elem for elem 
            in mults_dict[self.config.vars.sp_mult[1]][::-1]
            if "." not in elem]
        
        index_date_pb = [elem for elem 
                 in mults_dict[self.config.vars.sp_mult[2]][::-1] if "," in elem]

        df_ey_pe = pd.DataFrame({
            "Date": index_date_ey_pe, 
            "earning_yields": sp_ey,
            "price_earnings": sp_pe,
        })

        df_ey_pe["Date"] = pd.to_datetime(df_ey_pe["Date"])
        df_ey_pe["year"] = df_ey_pe["Date"].dt.year
        df_ey_pe.set_index("Date", inplace=True)


        df_pb = pd.DataFrame({
            "Date": index_date_pb, 
            "price_to_book": sp_pb,
        })

        df_pb["Date"] = pd.to_datetime(df_pb["Date"])
        df_pb["year"] = df_pb["Date"].dt.year
        df_pb.set_index("Date", inplace=True)

        return df_ey_pe, df_pb
    

    def get_economic_indicators(self) -> pd.DataFrame | list:
        """Download USA Economic
          Indicators"""

        ind_list = []

        for ind in self.config.vars.us_eco_ind:
            try:
                ind_series = pdr.DataReader(ind, "fred", self.start, self.end)
                if ind in ["CPIAUCSL", "PCE"]:
                    ind_series = ind_series.pct_change()
                ind_list.append(ind_series)

            except Exception as error:
                raise OSError(error) from error

        return ind_list
    

    def get_adamodar_data(self):
        """Scraps the adamodar 
        Default Spreads and Risks data"""

        def clean_list(lst, begin, step = 6):
            return [" ".join(lst[i].replace("\n", "").split()) for i in range(begin, len(lst) - (5 - begin), step)][:-1]

        try:
            response = requests.get(self.config.vars.adamodar_url)
            if not response.ok:
                raise FileNotFoundError("Could not requets the Adamodar Data")
            soup = BeautifulSoup(response.content, "html.parser")

            elems = soup.find_all("td")

            elems = [elem.text.strip() for elem in elems]
            elems = [elem for elem in elems[elems.index("Country"):]]

        except Exception as error:
            raise OSError(error) from error
        
        countrys = clean_list(elems, 0)
        adj_default_spread = clean_list(elems, 1)
        equity_risk = clean_list(elems, 2)
        country_risk_premium = clean_list(elems, 3)
        corporate_tax_rate = clean_list(elems, 4)
        moodys = clean_list(elems, 5)

        df_adamodar = pd.DataFrame([countrys, adj_default_spread, 
                                    equity_risk, country_risk_premium,
                                    corporate_tax_rate, moodys]).T
        
        df_adamodar.columns = df_adamodar.iloc[0]
        df_adamodar.drop(0, inplace=True)

        return df_adamodar
        

    def get_market_indicators(self) -> pd.DataFrame | list:
        """Downloads USA Market
          Indicators"""
        
        ind_list = []

        for ind in self.config.vars.us_mkt_ind:
            try:
                ind_series = self.fred.get_series(ind,
                                                  observation_start=self.start, 
                                                  observation_end=self.end)
                ind_series = ind_series.to_frame(name=ind)
                ind_series.index.name = "Date"
                ind_list.append(ind_series)
            except Exception as error:
                raise OSError(error) from error
            
        return ind_list


    def get_dxy_series(self) -> pd.DataFrame:
        """Downloads dolar 
        index series"""

        try:
            dxy = yf.download(self.config.vars.dxy, start=self.start, end=self.end)["Close"]

        except Exception as error:
            raise OSError(error) from error
        
        return dxy


    def get_mkt_returns(self) -> pd.DataFrame:
        """Downloads ff mkt-rf returns"""
        try:
            asset_series = pdr.DataReader(self.config.vars.equity_rf, "famafrench", self.start, self.end)[0]["Mkt-RF"]
            asset_series = asset_series.to_frame()
            asset_series.index.name = "Date"
            asset_series.index = asset_series.index.to_timestamp()
        except Exception as error:
            raise OSError(error) from error

        return asset_series
    

    def get_grain_prices(self) -> pd.DataFrame | list:
        """Download Commodities Prices"""
        
        comm_list = []

        for comm_ind in self.config.vars.grain_prices:
            try:
                comm = self.fred.get_series(comm_ind, observation_start=self.start, 
                                     observation_end=self.end)
                comm = comm.to_frame(name=comm_ind)
                comm_list.append(comm)
            except Exception as error:
                raise OSError(error) from error
            
        df_final = pd.concat(comm_list, axis=1)
        df_final.dropna
            
        return df_final
    
    def get_energy_prices(self) -> pd.DataFrame | list:
        """Download Commodities Prices"""
        
        comm_list = []

        for comm_ind in self.config.vars.energy_prices:
            try:
                comm = self.fred.get_series(comm_ind, observation_start=self.start, 
                                     observation_end=self.end)
                comm = comm.to_frame(name=comm_ind)
                comm_list.append(comm)
            except Exception as error:
                raise OSError(error) from error
            
        df_final = pd.concat(comm_list, axis=1)
        df_final.dropna
            
        return df_final
    
    def get_gsci_series(self) -> pd.DataFrame:
        """Downloads GSCI etf
        series"""
        
        try:
            gsci = yf.download(self.config.vars.gsci, start=self.start, end=self.end)["Close"]
        except Exception as error:
                raise OSError(error) from error

        return gsci
    
    def get_all_comm_index(self) -> pd.DataFrame:
        """Downloads gld 
        etf vol series"""
        
        try:
            all_comm = self.fred.get_series(self.config.vars.global_price_all_comm, observation_start=self.start, 
                                     observation_end=self.end)
            all_comm = all_comm.to_frame()
            all_comm.index.name = "Date"

        except Exception as error:
                raise OSError(error) from error
        
        return all_comm
    
    def get_gold_vol_series(self) -> pd.DataFrame:
        """Downloads gld 
        etf vol series"""
        
        try:
            gold_vol = self.fred.get_series(self.config.vars.gold_vol, observation_start=self.start, 
                                     observation_end=self.end)
            gold_vol = gold_vol.to_frame()
            gold_vol.index.name = "Date"

        except Exception as error:
                raise OSError(error) from error

        return gold_vol
    
    def get_comm_indexes(self) -> pd.DataFrame | list:
        """Download Commodities Indexes"""
        
        comm_list = []

        for comm_ind in self.config.vars.comm_indexes:
            try:
                comm = self.fred.get_series(comm_ind, observation_start=self.start, 
                                     observation_end=self.end)
                comm = comm.to_frame(name=comm_ind)
                comm_list.append(comm)
            except Exception as error:
                raise OSError(error) from error
            
        df_final = pd.concat(comm_list, axis=1)
        df_final.dropna
            
        return df_final
    
    def get_soy_series(self) -> pd.DataFrame:
        """Downloads soybean series"""
        
        try:
            soy = self.fred.get_series(self.config.vars.soy_price, observation_start=self.start, 
                                     observation_end=self.end)
            soy = soy.to_frame(name=self.config.vars.soy_price)
            soy.index.name = "Date"

        except Exception as error:
                raise OSError(error) from error

        return soy
            
        
    def get_emerging_data(self) -> pd.DataFrame | list:
        """Download Emerging
        Markets Data"""

        ind_list = []
        for ind in self.config.vars.em_mkt:
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
            emb = yf.download(self.config.vars.emb, start=self.start, end=self.end)["Close"]
        except Exception as error:
            raise OSError(error) from error
        
        print(emb)
        
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
            vxeem = self.fred.get_series(self.config.vars.em_etfs_vol,
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
            spdw = yf.download(self.config.vars.global_ex_us_etf, 
                        start=self.start, end=self.end)["Close"]

        except Exception as error:
            raise OSError(error) from error
        
        if len(spdw) == 0:
            spdw, metadata = self.av_tseries.get_daily("SPDW", outputsize="full")
            spdw.sort_index(inplace=True)
            spdw = spdw["4. close"]

        return spdw
    

    def get_br_implied_inflation(self) -> str:
        """Scrap Implied Inflation
        data for specific vertices"""

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
        
        df_implicita = pd.DataFrame({"Vértice": lista_vertices,
                                     "ETTJ PRE": lista_eetj_pre,
                                     "ETTJ NTNB": lista_eetj_ntnb,
                                     "Inflação Implicita": lista_inf_implicita})

        return df_implicita
    
# e= Extract()
# print(e.get_comm_indexes())
# print(e.get_sp_multiples())
# print(e.get_economic_indicators())
# print(e.get_market_indicators())
# print(e.get_dxy_series())
# print(e.get_mkt_returns())
# print(e.get_commodities())
# print(e.get_global_exus_data())
# print(e.get_br_implied_inflation())
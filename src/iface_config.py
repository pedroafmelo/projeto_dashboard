# -*- coding: UTF-8 -*-
"""Import modules"""

from os import environ
from os.path import join, dirname
from dataclasses import dataclass, field
from dotenv import load_dotenv
from yaml import load
from yaml.loader import SafeLoader
from streamlit import secrets


@dataclass
class Variables:
    """ Variables dataclass """
    
    # non_default
    data_dir: str
    img_dir: str
    icons_dir: str
    logo_bequest: str
    icone_bequest: str
    geopolitical_risk: str
    gdp_atlanta: str
    adamodar_url: str
    mult_base_url: str
    equity_rf: str
    dxy: str
    emb: str
    em_etfs_vol: str
    inf_implicita_br: str
    di_future: str
    ambima_holidays: str
    gsci: str
    gold_vol: str
    soy_price: str
    global_price_all_comm: str
    msci_eur_mult: str
    global_ex_us_etf: str

    FRED_API_KEY: str
    AV_API_KEY: str

    # default
    sp_mult: list = field(default_factory=list)

    us_eco_ind: list = field(default_factory=list)

    us_bonds_yields: list = field(default_factory=list)

    us_mkt_ind: list = field(default_factory=list)
    
    em_mkt: list = field(default_factory=list)

    grain_prices: list = field(default_factory=list)
    energy_prices: list = field(default_factory=list)
    comm_indexes: list = field(default_factory=list)



class Config:
    """Configuration Interface"""

    def __init__(self) -> None:
        """Load instance Variables"""
        data = {}
        with open(join(dirname(__file__), "env.yaml"), encoding="utf-8") as file:
            data=load(file, Loader=SafeLoader)

        load_dotenv()

        self.vars = Variables(
                data_dir=data.get("data_dir"),
                img_dir=data.get("img_dir"),
                logo_bequest=data.get("logo_bequest"),
                icone_bequest=data.get("icone_bequest"),
                icons_dir=data.get("icons_dir"),
                sp_mult=[
                    data.get("sp_earnings_yields"), 
                    data.get("sp_pe"),
                    data.get("sp_pb"), 
                    ],
                mult_base_url=data.get("mult_base_url"),
                us_eco_ind = [
                    data.get("ind_production"),
                    data.get("cpi_urban"),
                    data.get("pce"),
                    data.get("implied_inflation"),
                    data.get("gdp_now")
                    ],
                geopolitical_risk=data.get("geopolitical_risk"),
                gdp_atlanta=data.get("gdp_atlanta"),
                adamodar_url=data.get("adamodar_url"),
                us_bonds_yields = [
                    data.get("2_y"),
                    data.get("5_y"),
                    data.get("10_y"),
                    data.get("20_y"),
                    data.get("30_y"),
                   ],

                us_mkt_ind = [
                    data.get("liquidity_spread"),
                    data.get("ice_bofa_hy_spread"),
                    data.get("ice_bofa_cred_spread"),
                    data.get("chicago_fci"),
                    data.get("leverage_subindex"),
                    data.get("risk_subindex"),
                    data.get("credit_subindex"),
                    ],
                equity_rf=data.get("equity-rf"),
                dxy=data.get("dxy"),
                gsci = data.get("gsci"),
                gold_vol=data.get("gold_vol"),
                grain_prices = [
                    data.get("wheat_price"),
                    data.get("corn_global_price")
                    ],

                soy_price=data.get("soy_global_price"),
                energy_prices=[ 
                    data.get("brent_oil_price"),
                    data.get("wti_oil_price"),
                    data.get("henry_pub_ng_price")
                    ],
                comm_indexes=[
                    data.get("global_price_energy"),
                    data.get("grains_export_price_index")
                    ],
                global_price_all_comm=data.get("global_price_all_comm"),
                em_mkt = [
                    data.get("ice_bofa_hy_em_spread"),
                    data.get("ice_bofa_cred_em_spread"),
                    data.get("em_non_fin_ice_bofa"),
                    data.get("asia_em_bofa"),
                    data.get("latin_em_bofa"),
                    data.get("euro_em_bofa"),
                   ],
                em_etfs_vol=data.get("em_etfs_vol"),
                emb=data.get("emb"),
                inf_implicita_br=data.get("inf_implicita_br"),
                ambima_holidays=data.get("ambima_holidays"),
                di_future=data.get("di_future"),
                msci_eur_mult=data.get("msci_eur_mult"),
                global_ex_us_etf=data.get("global_ex_us_etf"),

                FRED_API_KEY=secrets["general"]["FRED_API_KEY"],
                # FRED_API_KEY="XXX",
                # AV_API_KEY="YYY"
                AV_API_KEY=secrets["general"]["AV_API_KEY"]
        )
        self.base_color = "#fba725"

        self.app_names = ["Leonardo Quaranta", "Matheus Marinho", 
                          "Gabriel Basso", "Eliseu Batista", "Augusto Alves"]
        
        self.app_usernames = ["leoquaranta", "mmarinho", 
                              "gbasso", "eliseubat", "augalves"]
    

    def __repr__(self) -> str:
        """ Basic class
        representation """

        return str(self.vars)
    
    def __str__(self) -> str:
        """ Print
        representation """

        return str(self.vars)
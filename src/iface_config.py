# -*- coding: UTF-8 -*-
"""Import modules"""

from os import environ
from os.path import join, dirname
from dataclasses import dataclass
from dotenv import load_dotenv
from yaml import load
from yaml.loader import SafeLoader


@dataclass
class Variables:
    """ Variables dataclass """
    
    # paths and extensions
    data_dir: str
    img_dir: str

    # Asset Classes Returns (USA)
    equity: str
    credits: str
    high_yields: str

    # S&P500 Multiples
    mult_base_url: str
    sp_earnings_yields: str
    sp_pe: str
    sp_pb: str
    sp_fpe: str

    # Economics Indicators
    ind_production: str
    cpi_urban: str
    pce: str
    implied_inflation: str
    geopolitical_risk: str

    # USA Bonds Yields
    t_2_y: str
    t_5_y: str
    t_10_y: str
    t_20_y: str
    t_30_y: str

    # USA Market indicators
    liquidity_spread: str
    ice_bofa_spread: str
    chicago_fci: str
    leverage_subindex: str
    risk_subindex: str
    non_financial_leverage: str
    dxy: str

    # Commodities
    gsci: str
    agriculture_index: str
    oil_gas: str

    # Emerging Markets
    emb: str
    eem_multiples_site: str
    iemg_historical: str

    FRED_API_KEY: str


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
                equity=data.get("equity"),
                credits=data.get("credits"),
                high_yields=data.get("high_yields"),
                mult_base_url=data.get("mult_base_url"),
                sp_earnings_yields=data.get("sp_earnings_yields"),
                sp_pe=data.get("sp_pe"),
                sp_pb=data.get("sp_pb"),
                sp_fpe=data.get("sp_fpe"),
                ind_production=data.get("ind_production"),
                cpi_urban=data.get("cpi_urban"),
                pce=data.get("pce"),
                implied_inflation=data.get("implied_inflation"),
                geopolitical_risk=data.get("geopolitical_risk"),
                t_2_y=data.get("2_y"),
                t_5_y=data.get("5_y"),
                t_10_y=data.get("10_y"),
                t_20_y=data.get("20_y"),
                t_30_y=data.get("30_y"),
                liquidity_spread=data.get("liquidity_spread"),
                ice_bofa_spread=data.get("ice_bofa_spread"),
                chicago_fci=data.get("chicago_fci"),
                leverage_subindex=data.get("leverage_subindex"),
                risk_subindex=data.get("risk_subindex"),
                non_financial_leverage=data.get("non_financial_leverage"),
                dxy=data.get("dxy"),
                gsci=data.get("gsci"),
                agriculture_index=data.get("agriculture_index"),
                oil_gas=data.get("oil_gas"),
                emb=data.get("emb"),
                eem_multiples_site=data.get("eem_multiples_site"),
                iemg_historical=data.get("iemg_historical"),

                FRED_API_KEY=environ["FRED_API_KEY"]
        )

    def __repr__(self) -> str:
        """ Basic class
        representation """

        return str(self.vars)
    
    def __str__(self) -> str:
        """ Print
        representation """

        return str(self.vars)
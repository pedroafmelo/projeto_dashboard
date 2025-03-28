# -*- coding: UTF-8 -*-
"""Import modules"""

from os import environ
from os.path import join, dirname
from dataclasses import dataclass, field
from dotenv import load_dotenv
from yaml import load
from yaml.loader import SafeLoader
from streamlit import secrets



class Indicators:

    """Indicators IDS Interface"""

    def __init__(self) -> None:
        """Load instance Variables"""
        
        indicators = {}
        ids = {}

        with open(join(dirname(__file__), "indicators.yaml"), encoding="utf-8") as file:
            data=load(file, Loader=SafeLoader)

        for indicator in data:
            indicators[indicator] = {data[indicator]["name"]: {
                    "id": data[indicator]["id"],
                    "description": data[indicator]["description"]
                }
            }
        
        for indicator in data:
            ids[indicator] = data[indicator]["id"]

        self.all_dict = data
        self.indicators = indicators
        self.ids = ids

        self.groups = {
            "us_macro_act_hist": [
                "imf_gdp",
                "ind_production",
                "retail_sales",
                "auxilio_desemprego_eua",
                "consumer_conf",
            ],
            "us_macro_act_for": [
                "imf_gdp",
                "advanced_retail_sales",
                "gdp_now_atlanta",
                "gdp_now_ny",
                "dsge"
            ],
            "us_macro_inf_hist": [
                "cpi_urban",
                "pce",
                "us_hpi",
                "inf_core"
            ],
            "us_macro_inf_for": [
                "imf_cpi",
                "5_implied_inflation",
                "10_implied_inflation",
                "michigan_inflation_expec"
            ],
            "us_macro_ffr": [
                "fed_funds",
                "cme_target_rate_pro",
                "taxa_juros_real_natural"
            ],
            "us_mkt_fin": [
                "chicago_fci",
                "leverage_subindex",
                "risk_subindex",
                "credit_subindex",
            ],
            "us_mkt_cred_spread": [
                "ice_bofa_cred_spread",
                "ice_bofa_hy_spread",
            ],
            "us_mkt_int_rates": [
                "spread_10y_2y",
                "2_y",
                "5_y",
                "10_y",
                "20_y",
                "30_y",
                "us_yield_curve"
            ],
            "us_mkt_extras": [
                "dxy",
                "equity-rf",
                "indice_vix"
            ],
            "us_mkt_prices_hist": [
                "sp_earnings_yields",
                "sp_pe",
                "sp_pb"
            ],
            "br_macro_act_hist": [
                "imf_gdp",
                "ibcbr",
                "producao_industrial",
                "vendas_varejo",
                "inec_ano_corrente",
                "inec_compras",
                "inec_renda_pessoal",
                "icei_condicoes"
            ],
            "br_macro_act_for": [
                "imf_gdp",
                "projecao_pib_bcb",
                "icei_expectativas"
            ],
            "br_macro_inf_hist": [
                "ipca",
                "igpm",
                "ipca_ms"
            ],
            "br_macro_inf_for": [
                "projecao_inflacao_bcb",
                "inf_implicita_br"
            ],
            "br_macro_selic": [
                "selic",
                "selic_real"
            ],
            "br_macro_focus": [
                "projecoes_focus"
            ],
            "br_mkt_investimento": [
                "investimento_estrangeiro",
                "investimento_institucional",
                "investimento_pf",
                "investimento_if",
                "investimento_outros"
            ],
            "br_mkt_juros": [
                "curva_juros_pre",
                "curva_juros_pos",
                "curva_juros_ipca"
            ],
            "br_mkt_preco": [
                "pl_ibovespa"
            ],
            "em_macro_act": [
                "imf_gdp",
                "pmi_paises"
            ],
            "em_macro_cpi": [
                "imf_cpi"
            ],
            "em_macro_juros": [
                "taxa_juros_pais"
            ],
            "em_macro_risco": [
                "adamodar_risk"
            ],
            "em_mkt_spread_cred": [
                "ice_bofa_hy_em_spread",
                "ice_bofa_cred_em_spread",
                "asia_em_bofa",
                "latin_em_bofa",
                "euro_em_bofa"
            ],
            "em_mkt_preco": [
                "msci_emerging_markets_pl",
            ],
            "em_mkt_extras": [
                "em_etfs_vol"
            ],
            "global_macro_act": [
                "imf_gdp",
                "pmi_paises"
            ],
            "global_macro_inf": [
                "imf_cpi"
            ],
            "global_macro_juros": [
                "taxa_juros_pais",
            ],
            "global_macro_risco": [
                "adamodar_risk"
            ],
            "global_mkt_preco": [
                "pl_dev_ex_us"
            ],
            "grain_prices": [
                "wheat_global_price",
                "corn_global_price",
                "soy_global_price"
            ],
            "energy_prices": [
                "brent_oil_price",
                "wti_oil_price",
                "henry_pub_ng_price",
            ],
            "gold": [
                "gold_vol",
                "gold_prices"
            ],
            "comm_indexes": [
                "gsci",
                "global_price_energy",
                "grains_export_price_index",
                "global_price_all_comm",
                "comm_br",
                "comm_br_metal",
                "comm_br_agro",
                "comm_br_energia"
            ],
        }


    def get_theme_dict(self, theme_name: str) -> dict:
        """Gets a theme
        Return the correct dict"""

        return {
            name: value for id, dic in self.indicators.items() 
            for name, value in dic.items() if id in self.groups[theme_name]
            }
    

    def get_ids_list(self, theme_name: str):
        """Gets a theme
        Return the ids"""
        

        return [id for ind, id in self.ids.items()
                if ind in self.groups[theme_name]]

    
    def __repr__(self) -> str:
        """ Basic class
        representation """

        return str(self.vars)
    
    def __str__(self) -> str:
        """ Print
        representation """

        return str(self.vars)
    
ind = Indicators()
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
    
    data_dir: str 
    img_dir: str
    logo_bequest: str
    logo_pleno: str
    icons_dir: str
    icone_bequest: str
    mult_base_url: str
    url_estimate_ey: str
    url_estimate_pe: str
    url_estimate_eps: str

    gdp_atlanta: str
    gdp_ny: str
    adamodar_url: str
    url_anbima_inf: str
    di_future: str
    anbima_holidays: str
    imf_gdp: str
    imf_cpi: str

    url_ouro: str
    url_dsge: str
    url_next_ffr_cme: str

    par_yield_curves_2024: str
    par_yield_curves_2025: str

    imf_gdp: str
    imf_cpi: str
    prod_industrial_url: str
    vendas_varejo_url: str
    relatorio_inflacao_url: str
    cds_5anos: str
    taxas_juros: str
    ipca_focus: str
    pib_focus: str
    selic_focus: str
    cambio_focus: str

    indice_hsi: str
    latin_am_msci: str
    taiwan_msci: str
    csi_300: str

    stoxx_600: str
    nikei_225: str

    FRED_API_KEY: str
    AV_API_KEY: str
    
    sp_mult_urls: list = field(default_factory=list)

class Config:

    """Configuration Interface"""

    def __init__(self) -> None:
        """Load instance Variables"""
        data = {}
        with open(join(dirname(__file__), "config.yaml"), encoding="utf-8") as file:
            data=load(file, Loader=SafeLoader)

        load_dotenv()

        self.vars = Variables(
                data_dir=data.get("data_dir"),
                img_dir=data.get("img_dir"),
                logo_bequest=data.get("logo_bequest"),
                logo_pleno=data.get("logo_pleno"),
                icone_bequest=data.get("icone_bequest"),
                icons_dir=data.get("icons_dir"),

                mult_base_url=data.get("mult_base_url"),

                sp_mult_urls = [
                    data.get("url_sp_ey"),
                    data.get("url_sp_pe"),
                    data.get("url_sp_pb")
                    ],
                url_estimate_ey=data.get("url_estimate_ey"),
                url_estimate_pe=data.get("url_estimate_pe"),
                url_estimate_eps=data.get("url_estimate_eps"),
                
                gdp_atlanta=data.get("gdp_atlanta"),
                gdp_ny=data.get("gdp_ny"),
                url_dsge=data.get("url_dsge"),

                par_yield_curves_2024=data.get("par_yield_curves_2024"),
                par_yield_curves_2025=data.get("par_yield_curves_2025"),
                
                url_next_ffr_cme=data.get("url_next_ffr_cme"),
                
                adamodar_url=data.get("adamodar_url"),
                
                url_anbima_inf=data.get("url_anbima_inf"),
                anbima_holidays=data.get("anbima_holidays"),
                
                di_future=data.get("di_future"),
                
                imf_gdp=data.get("imf_gdp"),
                imf_cpi=data.get("imf_cpi"),
                
                url_ouro=data.get("url_ouro"),

                prod_industrial_url=data.get("prod_industrial_url"),
                vendas_varejo_url=data.get("vendas_varejo_url"),
                relatorio_inflacao_url=data.get("relatorio_inflacao_url"),
                cds_5anos=data.get("cds_5anos"),
                taxas_juros=data.get("taxas_juros"),
                ipca_focus=data.get("ipca_focus"),
                pib_focus=data.get("pib_focus"),
                selic_focus=data.get("selic_focus"),
                cambio_focus=data.get("cambio_focus"),

                indice_hsi=data.get("indice_hsi"),
                latin_am_msci=data.get("latin_am_msci"),
                taiwan_msci=data.get("taiwan_msci"),
                csi_300=data.get("csi_300"),

                stoxx_600=data.get("stoxx_600"),
                nikei_225=data.get("nikei_225"),

                # FRED_API_KEY=secrets["general"]["FRED_API_KEY"],
                FRED_API_KEY="97d32927fcbb695624a531ded0e8bf4b",
                AV_API_KEY="YYY"
                # AV_API_KEY=secrets["general"]["AV_API_KEY"]
        )
        self.base_color = "#fba725"
        self.multiple_color = ["#dd4f00", "#983f4a", "#ffae42", "#ffffff", "#ffba6a"]

        self.app_names = ["Leonardo Quaranta", "Matheus Marinho", 
                          "Gabriel Basso", "Eliseu Batista", "Augusto Alves"]
        
        self.app_usernames = ["leoquaranta", "mmarinho", 
                              "gbasso", "eliseubat", "augalves"]
        
        self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        

    def __repr__(self) -> str:
        """ Basic class
        representation """

        return str(self.vars)
    
    def __str__(self) -> str:
        """ Print
        representation """

        return str(self.vars)
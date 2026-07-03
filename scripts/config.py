from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_INTERIM = ROOT / "data" / "interim"
DATA_PROCESSED = ROOT / "data" / "processed"
DOCS = ROOT / "docs"
REPORTS = ROOT / "reports"

START_YEAR = 1960
LAG_BUFFER_START_YEAR = 1950
END_YEAR = 2026

DATAVERSE_API = "https://dataverse.nl/api"

DATAVERSE_FILES = {
    "pwt": {
        "persistent_id": "doi:10.34894/FABVLR",
        "filename": "pwt110.xlsx",
        "raw_path": DATA_RAW / "pwt" / "pwt110.xlsx",
        "source_url": "https://dataverse.nl/dataset.xhtml?persistentId=doi:10.34894/FABVLR",
    },
    "maddison": {
        "persistent_id": "doi:10.34894/INZBF2",
        "filename": "mpd2023_web.xlsx",
        "raw_path": DATA_RAW / "maddison" / "mpd2023_web.xlsx",
        "source_url": "https://dataverse.nl/dataset.xhtml?persistentId=doi:10.34894/INZBF2",
    },
}

WDI_INDICATORS = {
    "NY.GDP.MKTP.KD.ZG": "wdi_gdp_growth_annual_pct",
    "SP.POP.TOTL": "wdi_population",
    "NE.TRD.GNFS.ZS": "wdi_trade_gdp",
    "NE.GDI.FTOT.ZS": "wdi_investment_gdp",
    "NV.AGR.TOTL.ZS": "wdi_agriculture_value_added_gdp",
    "NV.IND.TOTL.ZS": "wdi_industry_value_added_gdp",
    "NV.SRV.TOTL.ZS": "wdi_services_value_added_gdp",
    "SP.URB.TOTL.IN.ZS": "wdi_urban_population_pct",
    "SP.DYN.LE00.IN": "wdi_life_expectancy",
}

WDI_SOURCE_URLS = {
    code: f"https://data.worldbank.org/indicator/{code}" for code in WDI_INDICATORS
}


def ensure_dirs() -> None:
    for path in [
        DATA_RAW / "pwt",
        DATA_RAW / "maddison",
        DATA_RAW / "wdi",
        DATA_INTERIM,
        DATA_PROCESSED,
        DOCS,
        REPORTS,
    ]:
        path.mkdir(parents=True, exist_ok=True)

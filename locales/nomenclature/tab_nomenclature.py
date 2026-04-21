"""Локалізація для вкладки номенклатури."""


tab_Nomenclature = {
    "uk": {"name": "Номенклатура"},
    "en": {"name": "Nomenclature"},
}


def name_for(locale: str) -> str:
    return tab_Nomenclature.get(locale, tab_Nomenclature["en"])["name"]

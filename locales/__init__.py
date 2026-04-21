CURRENT_LOCALE = "uk"


def get_locale() -> str:
    return CURRENT_LOCALE


def set_locale(lang: str) -> None:
    global CURRENT_LOCALE
    if lang in ("uk", "en"):
        CURRENT_LOCALE = lang
    else:
        raise ValueError(f"Unsupported locale: {lang}")


# Допоміжні функції вкладок імпортуються ліниво, щоб цей файл залишався мінімальним.
from .tab_cards import add_button_text_for as _cards_add_button_text_for
from .tab_cards import access_add_button_text_for as _cards_access_add_button_text_for
from .tab_cards import access_dialog_texts_for as _cards_access_dialog_texts_for
from .tab_cards import access_edit_button_text_for as _cards_access_edit_button_text_for
from .tab_cards import access_name_for as _cards_access_name_for
from .tab_cards import admission_add_button_text_for as _cards_admission_add_button_text_for
from .tab_cards import admission_dialog_texts_for as _cards_admission_dialog_texts_for
from .tab_cards import admission_edit_button_text_for as _cards_admission_edit_button_text_for
from .tab_cards import admission_name_for as _cards_admission_name_for
from .tab_cards import add_dialog_texts_for as _cards_add_dialog_texts_for
from .tab_cards import edit_button_text_for as _cards_edit_button_text_for
from .tab_cards import edit_dialog_texts_for as _cards_edit_dialog_texts_for
from .tab_cards import get_tab_cards_access_headers as _cards_access_headers
from .tab_cards import get_tab_cards_table_headers as _cards_table_headers
from .tab_cards import get_tab_cards_admission_headers as _cards_admission_headers
from .tab_cards import name_for as _cards_name_for
from .tab_cards import validation_error_title_for as _cards_validation_error_title_for


def get_tab_cards_name() -> str:
    return _cards_name_for(CURRENT_LOCALE)


def get_tab_cards_add_button_text() -> str:
    return _cards_add_button_text_for(CURRENT_LOCALE)


def get_tab_cards_edit_button_text() -> str:
    return _cards_edit_button_text_for(CURRENT_LOCALE)


def get_tab_cards_admission_add_button_text() -> str:
    return _cards_admission_add_button_text_for(CURRENT_LOCALE)


def get_tab_cards_admission_edit_button_text() -> str:
    return _cards_admission_edit_button_text_for(CURRENT_LOCALE)


def get_tab_cards_admission_name() -> str:
    return _cards_admission_name_for(CURRENT_LOCALE)


def get_tab_cards_admission_dialog_texts() -> dict:
    return _cards_admission_dialog_texts_for(CURRENT_LOCALE)


def get_tab_cards_access_add_button_text() -> str:
    return _cards_access_add_button_text_for(CURRENT_LOCALE)


def get_tab_cards_access_edit_button_text() -> str:
    return _cards_access_edit_button_text_for(CURRENT_LOCALE)


def get_tab_cards_access_name() -> str:
    return _cards_access_name_for(CURRENT_LOCALE)


def get_tab_cards_access_dialog_texts() -> dict:
    return _cards_access_dialog_texts_for(CURRENT_LOCALE)


def get_tab_cards_table_headers() -> list:
    return _cards_table_headers(CURRENT_LOCALE)


def get_tab_cards_admission_headers() -> list:
    return _cards_admission_headers(CURRENT_LOCALE)


def get_tab_cards_access_headers() -> list:
    return _cards_access_headers(CURRENT_LOCALE)


def get_tab_cards_add_dialog_texts() -> dict:
    return _cards_add_dialog_texts_for(CURRENT_LOCALE)


def get_tab_cards_edit_dialog_texts() -> dict:
    return _cards_edit_dialog_texts_for(CURRENT_LOCALE)


def get_tab_cards_validation_error_title() -> str:
    return _cards_validation_error_title_for(CURRENT_LOCALE)

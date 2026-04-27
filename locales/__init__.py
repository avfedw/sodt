"""Фасад локалізації застосунку з поточним активним кодом мови."""

CURRENT_LOCALE = "uk"


def get_locale() -> str:
    """Повертає код мови, який зараз використовують UI-компоненти."""

    return CURRENT_LOCALE


def set_locale(lang: str) -> None:
    """Змінює активну локаль, якщо вона підтримується застосунком."""

    global CURRENT_LOCALE
    if lang in ("uk", "en"):
        CURRENT_LOCALE = lang
    else:
        raise ValueError(f"Unsupported locale: {lang}")


from .cards.tab_cards import add_button_text_for as _cards_add_button_text_for
from .cards.tab_cards import cards_visibility_filter_options_for as _cards_visibility_filter_options_for
from .cards.tab_cards import access_add_button_text_for as _cards_access_add_button_text_for
from .cards.tab_cards import access_dialog_texts_for as _cards_access_dialog_texts_for
from .cards.tab_cards import access_edit_button_text_for as _cards_access_edit_button_text_for
from .cards.tab_cards import access_name_for as _cards_access_name_for
from .cards.tab_cards import admission_add_button_text_for as _cards_admission_add_button_text_for
from .cards.tab_cards import admission_dialog_texts_for as _cards_admission_dialog_texts_for
from .cards.tab_cards import admission_edit_button_text_for as _cards_admission_edit_button_text_for
from .cards.tab_cards import admission_name_for as _cards_admission_name_for
from .cards.tab_cards import add_dialog_texts_for as _cards_add_dialog_texts_for
from .cards.tab_cards import edit_button_text_for as _cards_edit_button_text_for
from .cards.tab_cards import edit_dialog_texts_for as _cards_edit_dialog_texts_for
from .cards.tab_cards import get_tab_cards_access_headers as _cards_access_headers
from .cards.tab_cards import get_tab_cards_table_headers as _cards_table_headers
from .cards.tab_cards import get_tab_cards_admission_headers as _cards_admission_headers
from .cards.tab_cards import name_for as _cards_name_for
from .cards.tab_cards import validation_error_title_for as _cards_validation_error_title_for
from .certificate14.tab_certificate14 import add_button_text_for as _certificate14_add_button_text_for
from .certificate14.tab_certificate14 import card_picker_texts_for as _certificate14_card_picker_texts_for
from .certificate14.tab_certificate14 import dialog_texts_for as _certificate14_dialog_texts_for
from .certificate14.tab_certificate14 import edit_button_text_for as _certificate14_edit_button_text_for
from .certificate14.tab_certificate14 import empty_state_for as _certificate14_empty_state_for
from .certificate14.tab_certificate14 import export_button_text_for as _certificate14_export_button_text_for
from .certificate14.tab_certificate14 import export_dialog_texts_for as _certificate14_export_dialog_texts_for
from .certificate14.tab_certificate14 import headers_for as _certificate14_headers_for
from .certificate14.tab_certificate14 import name_for as _certificate14_name_for
from .certificate14.tab_certificate14 import refresh_button_text_for as _certificate14_refresh_button_text_for
from .certificate14.tab_certificate14 import validation_error_title_for as _certificate14_validation_error_title_for
from .assignment_history.tab_assignment_history import empty_state_for as _assignment_history_empty_state_for
from .assignment_history.tab_assignment_history import headers_for as _assignment_history_headers_for
from .assignment_history.tab_assignment_history import name_for as _assignment_history_name_for
from .assignment_history.tab_assignment_history import person_filter_placeholder_for as _assignment_history_person_filter_placeholder_for
from .assignment_history.tab_assignment_history import position_filter_placeholder_for as _assignment_history_position_filter_placeholder_for
from .assignment_history.tab_assignment_history import refresh_button_text_for as _assignment_history_refresh_button_text_for
from .nomenclature.tab_nomenclature import add_button_text_for as _nomenclature_add_button_text_for
from .nomenclature.tab_nomenclature import card_picker_texts_for as _nomenclature_card_picker_texts_for
from .nomenclature.tab_nomenclature import dialog_texts_for as _nomenclature_dialog_texts_for
from .nomenclature.tab_nomenclature import edit_button_text_for as _nomenclature_edit_button_text_for
from .nomenclature.tab_nomenclature import empty_state_for as _nomenclature_empty_state_for
from .nomenclature.tab_nomenclature import headers_for as _nomenclature_headers_for
from .nomenclature.tab_nomenclature import name_for as _nomenclature_name_for
from .nomenclature.tab_nomenclature import refresh_button_text_for as _nomenclature_refresh_button_text_for
from .nomenclature.tab_nomenclature import validation_error_title_for as _nomenclature_validation_error_title_for
from .structure.tab_structure import add_button_text_for as _structure_add_button_text_for
from .structure.tab_structure import add_child_button_text_for as _structure_add_child_button_text_for
from .structure.tab_structure import delete_button_text_for as _structure_delete_button_text_for
from .structure.tab_structure import dialog_texts_for as _structure_dialog_texts_for
from .structure.tab_structure import edit_button_text_for as _structure_edit_button_text_for
from .structure.tab_structure import empty_state_text_for as _structure_empty_state_text_for
from .structure.tab_structure import headers_for as _structure_headers_for
from .structure.tab_structure import name_for as _structure_name_for
from .structure.tab_structure import type_labels_for as _structure_type_labels_for
from .structure.tab_structure import validation_error_title_for as _structure_validation_error_title_for
from .settings.tab_settings import description_for as _settings_description_for
from .settings.tab_settings import export_button_text_for as _settings_export_button_text_for
from .settings.tab_settings import file_dialog_texts_for as _settings_file_dialog_texts_for
from .settings.tab_settings import import_button_text_for as _settings_import_button_text_for
from .settings.tab_settings import messages_for as _settings_messages_for
from .settings.tab_settings import name_for as _settings_name_for
from .settings.tab_settings import title_for as _settings_title_for


def get_tab_cards_name() -> str:
    """Повертає локалізовану назву вкладки карток."""

    return _cards_name_for(CURRENT_LOCALE)


def get_tab_cards_add_button_text() -> str:
    return _cards_add_button_text_for(CURRENT_LOCALE)


def get_tab_cards_edit_button_text() -> str:
    return _cards_edit_button_text_for(CURRENT_LOCALE)


def get_tab_cards_visibility_filter_options() -> list[str]:
    return _cards_visibility_filter_options_for(CURRENT_LOCALE)


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


def get_tab_certificate14_name() -> str:
    return _certificate14_name_for(CURRENT_LOCALE)


def get_tab_certificate14_add_button_text() -> str:
    return _certificate14_add_button_text_for(CURRENT_LOCALE)


def get_tab_certificate14_refresh_button_text() -> str:
    return _certificate14_refresh_button_text_for(CURRENT_LOCALE)


def get_tab_certificate14_edit_button_text() -> str:
    return _certificate14_edit_button_text_for(CURRENT_LOCALE)


def get_tab_certificate14_export_button_text() -> str:
    return _certificate14_export_button_text_for(CURRENT_LOCALE)


def get_tab_certificate14_empty_state_text() -> str:
    return _certificate14_empty_state_for(CURRENT_LOCALE)


def get_tab_certificate14_headers() -> list[str]:
    return _certificate14_headers_for(CURRENT_LOCALE)


def get_tab_certificate14_validation_error_title() -> str:
    return _certificate14_validation_error_title_for(CURRENT_LOCALE)


def get_tab_certificate14_dialog_texts() -> dict:
    return _certificate14_dialog_texts_for(CURRENT_LOCALE)


def get_tab_certificate14_card_picker_texts() -> dict:
    return _certificate14_card_picker_texts_for(CURRENT_LOCALE)


def get_tab_certificate14_export_dialog_texts() -> dict:
    return _certificate14_export_dialog_texts_for(CURRENT_LOCALE)


def get_tab_assignment_history_name() -> str:
    return _assignment_history_name_for(CURRENT_LOCALE)


def get_tab_assignment_history_refresh_button_text() -> str:
    return _assignment_history_refresh_button_text_for(CURRENT_LOCALE)


def get_tab_assignment_history_empty_state_text() -> str:
    return _assignment_history_empty_state_for(CURRENT_LOCALE)


def get_tab_assignment_history_position_filter_placeholder() -> str:
    return _assignment_history_position_filter_placeholder_for(CURRENT_LOCALE)


def get_tab_assignment_history_person_filter_placeholder() -> str:
    return _assignment_history_person_filter_placeholder_for(CURRENT_LOCALE)


def get_tab_assignment_history_headers() -> list[str]:
    return _assignment_history_headers_for(CURRENT_LOCALE)


def get_tab_nomenclature_name() -> str:
    return _nomenclature_name_for(CURRENT_LOCALE)


def get_tab_nomenclature_add_button_text() -> str:
    return _nomenclature_add_button_text_for(CURRENT_LOCALE)


def get_tab_nomenclature_refresh_button_text() -> str:
    return _nomenclature_refresh_button_text_for(CURRENT_LOCALE)


def get_tab_nomenclature_edit_button_text() -> str:
    return _nomenclature_edit_button_text_for(CURRENT_LOCALE)


def get_tab_nomenclature_empty_state_text() -> str:
    return _nomenclature_empty_state_for(CURRENT_LOCALE)


def get_tab_nomenclature_headers() -> list[str]:
    return _nomenclature_headers_for(CURRENT_LOCALE)


def get_tab_nomenclature_validation_error_title() -> str:
    return _nomenclature_validation_error_title_for(CURRENT_LOCALE)


def get_tab_nomenclature_dialog_texts() -> dict:
    return _nomenclature_dialog_texts_for(CURRENT_LOCALE)


def get_tab_nomenclature_card_picker_texts() -> dict:
    return _nomenclature_card_picker_texts_for(CURRENT_LOCALE)


def get_tab_structure_name() -> str:
    return _structure_name_for(CURRENT_LOCALE)


def get_tab_structure_add_button_text() -> str:
    return _structure_add_button_text_for(CURRENT_LOCALE)


def get_tab_structure_add_child_button_text() -> str:
    return _structure_add_child_button_text_for(CURRENT_LOCALE)


def get_tab_structure_edit_button_text() -> str:
    return _structure_edit_button_text_for(CURRENT_LOCALE)


def get_tab_structure_delete_button_text() -> str:
    return _structure_delete_button_text_for(CURRENT_LOCALE)


def get_tab_structure_empty_state_text() -> str:
    return _structure_empty_state_text_for(CURRENT_LOCALE)


def get_tab_structure_headers() -> list[str]:
    return _structure_headers_for(CURRENT_LOCALE)


def get_tab_structure_validation_error_title() -> str:
    return _structure_validation_error_title_for(CURRENT_LOCALE)


def get_tab_settings_name() -> str:
    return _settings_name_for(CURRENT_LOCALE)


def get_tab_settings_title_text() -> str:
    return _settings_title_for(CURRENT_LOCALE)


def get_tab_settings_description_text() -> str:
    return _settings_description_for(CURRENT_LOCALE)


def get_tab_settings_export_button_text() -> str:
    return _settings_export_button_text_for(CURRENT_LOCALE)


def get_tab_settings_import_button_text() -> str:
    return _settings_import_button_text_for(CURRENT_LOCALE)


def get_tab_settings_file_dialog_texts() -> dict:
    return _settings_file_dialog_texts_for(CURRENT_LOCALE)


def get_tab_settings_messages() -> dict:
    return _settings_messages_for(CURRENT_LOCALE)


def get_tab_structure_dialog_texts() -> dict:
    return _structure_dialog_texts_for(CURRENT_LOCALE)


def get_tab_structure_type_labels() -> dict[str, str]:
    return _structure_type_labels_for(CURRENT_LOCALE)

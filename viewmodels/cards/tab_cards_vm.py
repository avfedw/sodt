"""ViewModel для вкладки Cards з місцем для логіки MVVM."""

from db import CardsRepository


class TabCardsViewModel:
    def __init__(self):
        # ViewModel лишається тонким фасадом між UI та репозиторієм:
        # він зберігає тексти інтерфейсу й прокидує виклики даних без Qt-залежностей.
        self.repository = CardsRepository()

        self._load_texts()

        # Тут додаються спостережувані властивості, доступ до даних і команди

    def _load_texts(self):
        """Завантажує локалізовані тексти, а при збої використовує резервні значення."""

        # Лінивий імпорт, щоб уникнути циклічних залежностей під час завантаження модулів
        try:
            from locales import (
                get_tab_cards_add_button_text,
                get_tab_cards_access_add_button_text,
                get_tab_cards_access_dialog_texts,
                get_tab_cards_access_edit_button_text,
                get_tab_cards_access_headers,
                get_tab_cards_access_name,
                get_tab_cards_admission_add_button_text,
                get_tab_cards_admission_dialog_texts,
                get_tab_cards_admission_edit_button_text,
                get_tab_cards_admission_headers,
                get_tab_cards_admission_name,
                get_tab_cards_add_dialog_texts,
                get_tab_cards_edit_dialog_texts,
                get_tab_cards_name,
                get_tab_cards_table_headers,
                get_tab_cards_visibility_filter_options,
                get_tab_cards_validation_error_title,
            )

            self._apply_text_bundle(
                title=get_tab_cards_name(),
                add_button_text=get_tab_cards_add_button_text(),
                cards_visibility_filter_options=get_tab_cards_visibility_filter_options(),
                access_table_title=get_tab_cards_access_name(),
                add_access_button_text=get_tab_cards_access_add_button_text(),
                edit_access_button_text=get_tab_cards_access_edit_button_text(),
                access_dialog_texts=get_tab_cards_access_dialog_texts(),
                access_headers=get_tab_cards_access_headers(),
                admission_table_title=get_tab_cards_admission_name(),
                add_admission_button_text=get_tab_cards_admission_add_button_text(),
                admission_dialog_texts=get_tab_cards_admission_dialog_texts(),
                admission_headers=get_tab_cards_admission_headers(),
                add_dialog_texts=get_tab_cards_add_dialog_texts(),
                edit_dialog_texts=get_tab_cards_edit_dialog_texts(),
                edit_admission_button_text=get_tab_cards_admission_edit_button_text(),
                table_headers=get_tab_cards_table_headers(),
                validation_error_title=get_tab_cards_validation_error_title(),
            )

        except Exception:
            # Якщо шар локалізації тимчасово недоступний або впаде на імпорті,
            # вкладка все одно має відкритися з резервним англомовним набором.
            self._apply_text_bundle(**self._fallback_text_bundle())

    def _apply_text_bundle(self, **texts):
        """Записує зібраний набір текстів у властивості ViewModel."""

        # Зберігаємо тексти як прості атрибути, щоб view зверталась до них напряму
        # без додаткових словників чи умов під час побудови інтерфейсу.
        for key, value in texts.items():
            setattr(self, key, value)

    def _fallback_text_bundle(self) -> dict:
        """Повертає англомовний резервний набір текстів, якщо локалізація недоступна."""

        # Цей словник дублює мінімально необхідний набір ключів,
        # який очікує view під час побудови всіх кнопок, таблиць і діалогів.
        return {
            "title": "Cards",
            "add_button_text": "Add",
            "cards_visibility_filter_options": ["only available", "all", "unavailable"],
            "access_table_title": "Access",
            "add_access_button_text": "Add access",
            "edit_access_button_text": "Edit",
            "access_dialog_texts": {
                "add_title": "Grant/revoke access",
                "edit_title": "Grant/revoke access",
                "access_date": "Date",
                "order_number": "Order number",
                "access_type": "Access",
                "access_type_options": ["ОВ", "ЦТ", "Т"],
                "status": "Status",
                "status_options": ["granted", "revoked"],
                "save": "Save",
                "cancel": "Cancel",
                "select_card_warning": "Select a card first.",
                "select_access_warning": "Select a row in the access table first.",
            },
            "access_headers": ["Date", "Order number", "Access", "Status"],
            "admission_table_title": "Admission",
            "add_admission_button_text": "Add admission",
            "admission_dialog_texts": {
                "add_title": "Grant/revoke admission",
                "edit_title": "Grant/revoke admission",
                "escort_number": "Escort number",
                "escort_date": "Escort date",
                "response_number": "Response number",
                "response_date": "Response date",
                "order_number": "Order number",
                "order_date": "Order date",
                "admission_form": "Admission form",
                "admission_form_options": ["F-1", "F-2", "F-3"],
                "default_admission_form": "F-2",
                "admission_status": "Status",
                "admission_status_options": ["granted", "revoked"],
                "empty_date": "Not specified",
                "save": "Save",
                "cancel": "Cancel",
                "select_card_warning": "Select a card first.",
                "select_admission_warning": "Select a row in the lower table first.",
            },
            "admission_headers": [
                "Escort number",
                "Escort date",
                "Response number",
                "Response date",
                "Order number",
                "Order date",
                "Admission form",
                "Status",
            ],
            "add_dialog_texts": {
                "title": "Add card",
                "surname": "Surname",
                "name": "Name",
                "patronymic": "Patronymic",
                "save": "Save",
                "cancel": "Cancel",
            },
            "edit_dialog_texts": {
                "title": "Edit card",
                "surname": "Surname",
                "name": "Name",
                "patronymic": "Patronymic",
                "number": "Number within letter",
                "card_date": "Card date",
                "workflow_status": "Status",
                "document_kind": "Document or event type",
                "document_number": "Document number",
                "document_date": "Document or event date",
                "document_target": "Sent to",
                "service_note": "Service note",
                "user_note": "Note",
                "inactive_state": "Card state",
                "inactive_messages": {
                    "surname_changed": "This card is inactive because a new current card was created after surname change.",
                    "sent": "The card has been sent. Editing is unavailable, but it can be marked as returned.",
                    "destroyed": "The card has been destroyed. Editing is unavailable.",
                },
                "empty_date": "Not specified",
                "send_button": "Send",
                "destroy_button": "Destroy",
                "return_button": "Mark as returned",
                "document_kind_options": [
                    ("", "Not specified"),
                    ("escort", "Escort"),
                    ("act", "Act"),
                    ("planned_cancellation", "Planned cancellation"),
                    ("planned_destruction", "Planned destruction"),
                ],
                "workflow_status_options": [
                    ("", "Not specified"),
                    ("на скасування", "For cancellation"),
                    ("на знищення", "For destruction"),
                    ("знищено", "Destroyed"),
                    ("відправлено", "Sent"),
                ],
                "send_dialog": {
                    "title": "Send card",
                    "number": "Escort number",
                    "date": "Escort date",
                    "target": "Institution",
                    "confirm": "Send",
                    "cancel": "Cancel",
                },
                "destroy_dialog": {
                    "title": "Destroy card",
                    "number": "Act number",
                    "date": "Act date",
                    "confirm": "Destroy",
                    "cancel": "Cancel",
                },
                "return_dialog": {
                    "title": "Return card",
                    "number": "Return letter number",
                    "date": "Return date",
                    "target": "Institution",
                    "confirm": "Return",
                    "cancel": "Cancel",
                },
                "save": "Save",
                "cancel": "Cancel",
            },
            "edit_admission_button_text": "Edit",
            "table_headers": [
                "Letter - Number",
                "Date",
                "Surname",
                "Name",
                "Patronymic",
                "Document / Event",
                "Status",
                "Note",
            ],
            "validation_error_title": "Validation error",
        }

    def get_tab_cards_table_headers(self):
        return self.table_headers

    def get_tab_cards_admission_headers(self):
        return []

    def get_cards(self):
        return self.repository.list_cards()

    def get_accesses(self, card_id: int):
        return self.repository.list_accesses(card_id)

    def get_admissions(self, card_id: int):
        return self.repository.list_admissions(card_id)

    def create_card(self, surname: str, name: str, patronymic: str):
        return self.repository.create_card(surname, name, patronymic)

    def create_admission(self, card_id: int, escort_number: str, escort_date: str, admission_form: str):
        return self.repository.create_admission(card_id, escort_number, escort_date, admission_form)

    def create_access(self, card_id: int, access_date: str, order_number: str, access_type: str, status: str):
        return self.repository.create_access(card_id, access_date, order_number, access_type, status)

    def update_admission(
        self,
        admission_id: int,
        escort_number: str,
        escort_date: str,
        response_number: str,
        response_date: str,
        order_number: str,
        order_date: str,
        admission_form: str,
        admission_status: str,
    ):
        return self.repository.update_admission(
            admission_id,
            escort_number,
            escort_date,
            response_number,
            response_date,
            order_number,
            order_date,
            admission_form,
            admission_status,
        )

    def update_access(self, access_id: int, access_date: str, order_number: str, access_type: str, status: str):
        return self.repository.update_access(access_id, access_date, order_number, access_type, status)

    def update_card(
        self,
        card_id: int,
        surname: str,
        name: str,
        patronymic: str,
        number: str,
        card_date: str,
        document_kind: str,
        document_number: str,
        document_date: str,
        document_target: str,
        user_note: str,
    ):
        return self.repository.update_card(
            card_id,
            surname,
            name,
            patronymic,
            number,
            card_date,
            document_kind,
            document_number,
            document_date,
            document_target,
            user_note,
        )

    def update_card_service_note(self, card_id: int, service_note: str):
        return self.repository.update_card_service_note(card_id, service_note)

    def send_card(self, card_id: int, document_number: str, document_date: str, document_target: str):
        return self.repository.send_card(card_id, document_number, document_date, document_target)

    def destroy_card(self, card_id: int, document_number: str, document_date: str):
        return self.repository.destroy_card(card_id, document_number, document_date)

    def return_card(self, card_id: int, document_number: str, document_date: str, document_target: str):
        return self.repository.return_card(card_id, document_number, document_date, document_target)



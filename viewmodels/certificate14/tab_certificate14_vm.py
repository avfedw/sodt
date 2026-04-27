"""ViewModel для вкладки довідки 14."""

from dataclasses import dataclass
from pathlib import Path

from db import CardsRepository, Certificate14Repository
from db.cards_repository import AdmissionRecord
from db.certificate14_repository import default_certificate_date, default_expiration_date
from export.certificate14_export import build_export_data, export_certificate14_documents


@dataclass(slots=True)
class Certificate14RowView:
    """Підготовлений для таблиці рядок довідки 14."""

    certificate_id: int
    card_id: int
    number: str
    certificate_date: str
    full_name: str
    expiration_date: str
    recipient_surname: str
    returned_mark: str
    note: str


class TabCertificate14ViewModel:
    """Координує тексти та роботу з довідками 14."""

    def __init__(self, repository: Certificate14Repository | None = None, cards_repository: CardsRepository | None = None):
        self.repository = repository or Certificate14Repository()
        self.cards_repository = cards_repository or CardsRepository()
        self._load_texts()

    def _load_texts(self):
        try:
            from locales import (
                get_tab_certificate14_add_button_text,
                get_tab_certificate14_card_picker_texts,
                get_tab_certificate14_dialog_texts,
                get_tab_certificate14_export_dialog_texts,
                get_tab_certificate14_export_button_text,
                get_tab_certificate14_edit_button_text,
                get_tab_certificate14_empty_state_text,
                get_tab_certificate14_headers,
                get_tab_certificate14_name,
                get_tab_certificate14_refresh_button_text,
                get_tab_certificate14_validation_error_title,
            )

            self.title = get_tab_certificate14_name()
            self.add_button_text = get_tab_certificate14_add_button_text()
            self.refresh_button_text = get_tab_certificate14_refresh_button_text()
            self.edit_button_text = get_tab_certificate14_edit_button_text()
            self.export_button_text = get_tab_certificate14_export_button_text()
            self.empty_state_text = get_tab_certificate14_empty_state_text()
            self.headers = get_tab_certificate14_headers()
            self.validation_error_title = get_tab_certificate14_validation_error_title()
            self.dialog_texts = get_tab_certificate14_dialog_texts()
            self.card_picker_texts = get_tab_certificate14_card_picker_texts()
            self.export_dialog_texts = get_tab_certificate14_export_dialog_texts()
        except Exception:
            self.title = "Certificate 14"
            self.add_button_text = "Add certificate"
            self.refresh_button_text = "Refresh"
            self.edit_button_text = "Edit"
            self.export_button_text = "Export"
            self.empty_state_text = "No certificate 14 records have been added yet."
            self.headers = ["Number", "Certificate date", "Full name", "Expiration date", "Recipient surname", "Returned", "Note"]
            self.validation_error_title = "Validation error"
            self.dialog_texts = {"select_row_warning": "Select a certificate 14 record first."}
            self.card_picker_texts = {"select_card_warning": "Select a card first."}
            self.export_dialog_texts = {
                "select_rows_warning": "Select one or more certificate 14 records first.",
                "save_title": "Export certificate 14",
                "save_filter": "Word files (*.docx);;All files (*.*)",
                "default_file_name": "certificate14.docx",
                "success_title": "Completed",
                "success_message": "Certificates 14 exported successfully.",
            }

    def get_rows(self) -> list[Certificate14RowView]:
        return [self._build_row_view(record) for record in self.repository.list_records()]

    def card_options(self) -> list:
        busy_card_ids = self.repository.list_active_card_ids()
        cards = self.cards_repository.list_cards()
        available_cards = [
            card
            for card in cards
            if card.is_current and card.lifecycle_state != "destroyed" and card.card_id not in busy_card_ids
        ]
        return sorted(
            available_cards,
            key=lambda card: (card.surname.casefold(), card.name.casefold(), card.patronymic.casefold(), card.card_id),
        )

    def create_record(self, card):
        return self.repository.create_record(
            card.card_id,
            "",
            default_certificate_date(),
            card.surname,
            card.name,
            card.patronymic,
            default_expiration_date(),
            "",
            "",
        )

    def update_record(self, certificate_id: int, certificate_number: str, certificate_date: str, expiration_date: str, recipient_surname: str, is_returned: bool, note: str):
        return self.repository.update_record(
            certificate_id,
            certificate_number,
            certificate_date,
            expiration_date,
            recipient_surname,
            is_returned,
            note,
        )

    def export_records(self, certificate_ids: list[int], destination_path: str | Path) -> Path:
        if not certificate_ids:
            raise ValueError(self.export_dialog_texts["select_rows_warning"])

        records_by_id = {
            record.certificate_id: record
            for record in self.repository.list_records()
        }
        cards_by_id = {
            card.card_id: card
            for card in self.cards_repository.list_cards()
        }

        export_records = []
        for certificate_id in certificate_ids:
            record = records_by_id.get(certificate_id)
            if record is None:
                raise ValueError("Не вдалося знайти одну з вибраних довідок 14.")
            card = cards_by_id.get(record.card_id)
            if card is None:
                raise ValueError(f"Не вдалося знайти картку для довідки № {record.certificate_number}.")

            admission = self._pick_export_admission(record.card_id)
            export_records.append(
                build_export_data(
                    full_name=" ".join(part for part in (record.surname, record.name, record.patronymic) if part),
                    certificate_number=record.certificate_number,
                    certificate_date=record.certificate_date,
                    expiration_date=record.expiration_date,
                    admission_form=admission.admission_form if admission is not None else card.form,
                    order_number=admission.order_number if admission is not None else "",
                    order_date=admission.order_date if admission is not None else "",
                )
            )

        return export_certificate14_documents(export_records, destination_path)

    def _pick_export_admission(self, card_id: int) -> AdmissionRecord | None:
        admissions = self.cards_repository.list_admissions(card_id)
        granted_admissions = [
            admission
            for admission in admissions
            if admission.admission_status in {"надано", "granted"}
        ]
        source = granted_admissions if granted_admissions else admissions
        return source[-1] if source else None

    def _build_row_view(self, record) -> Certificate14RowView:
        full_name = " ".join(part for part in (record.surname, record.name, record.patronymic) if part)
        return Certificate14RowView(
            certificate_id=record.certificate_id,
            card_id=record.card_id,
            number=record.certificate_number,
            certificate_date=record.certificate_date,
            full_name=full_name,
            expiration_date=record.expiration_date,
            recipient_surname=record.recipient_surname,
            returned_mark="Так" if record.is_returned else "Ні",
            note=record.note,
        )
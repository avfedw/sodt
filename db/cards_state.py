"""Допоміжна логіка для похідного стану карток."""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable, Mapping, Any


_GRANTED_STATUSES = {"надано", "granted"}
_REVOKED_STATUSES = {"скасовано", "revoked"}


@dataclass(slots=True, frozen=True)
class AdmissionState:
    """Похідний стан допуску для однієї картки."""

    form: str = ""
    has_active: bool = False
    revoked_after_grant: bool = False
    revoked_date: str = ""
    reissue_date: str = ""


@dataclass(slots=True, frozen=True)
class AccessState:
    """Похідний стан доступу для однієї картки."""

    has_active: bool = False
    revoked_after_grant: bool = False
    revoked_date: str = ""


def build_admission_state_by_card_id(rows: Iterable[Mapping[str, Any]]) -> dict[int, AdmissionState]:
    """Будує поточний стан допуску для кожної картки за історією розпоряджень."""

    admission_state_by_card_id: dict[int, AdmissionState] = {}
    active_sequences_by_card_id: dict[int, list[tuple[int, str]]] = {}

    # Спочатку впорядковуємо історію, щоб однаково обробляти записи незалежно від того,
    # у якому порядку їх повернула база або сформували тести.
    sorted_rows = sorted(
        rows,
        key=lambda row: (
            _sort_key_from_date(str(row["order_date"])),
            int(row["id"]),
        ),
    )

    for row in sorted_rows:
        card_id = int(row["card_id"])
        admission_status = str(row["admission_status"])
        current_state = admission_state_by_card_id.get(card_id, AdmissionState())

        if admission_status in _GRANTED_STATUSES:
            # Для переоформлення важливий безперервний ланцюжок наданих форм,
            # тому зберігаємо не лише останню форму, а і шлях до неї.
            current_sequence = active_sequences_by_card_id.get(card_id, [])
            form_level = _admission_form_level(str(row["admission_form"]))
            if form_level is not None:
                current_sequence.append((form_level, str(row["order_date"])))
            active_sequences_by_card_id[card_id] = current_sequence
            admission_state_by_card_id[card_id] = AdmissionState(
                form=str(row["admission_form"]),
                has_active=True,
                reissue_date=_build_reissue_date(current_sequence),
            )
            continue

        if admission_status in _REVOKED_STATUSES and current_state.form:
            # Скасування обриває поточний ланцюжок, бо наступне надання вже має
            # рахуватися як новий цикл допуску, а не продовження старого.
            active_sequences_by_card_id[card_id] = []
            admission_state_by_card_id[card_id] = AdmissionState(
                form=current_state.form,
                revoked_after_grant=True,
                revoked_date=str(row["order_date"]),
            )

    return admission_state_by_card_id


def build_access_state_by_card_id(rows: Iterable[Mapping[str, Any]]) -> dict[int, AccessState]:
    """Будує поточний стан доступу для кожної картки за історією доступів."""

    access_state_by_card_id: dict[int, AccessState] = {}

    # Логіка доступів теж залежить від хронології: важливо знати,
    # чи було скасування саме після надання, а не само по собі.
    sorted_rows = sorted(
        rows,
        key=lambda row: (
            _sort_key_from_date(str(row["access_date"])),
            int(row["id"]),
        ),
    )

    for row in sorted_rows:
        card_id = int(row["card_id"])
        access_status = str(row["status"])
        current_state = access_state_by_card_id.get(card_id, AccessState())

        if access_status in _GRANTED_STATUSES:
            access_state_by_card_id[card_id] = AccessState(has_active=True)
            continue

        if access_status in _REVOKED_STATUSES and current_state.has_active:
            # Лише скасування активного доступу запускає службовий стан
            # "на скасування" для самої картки.
            access_state_by_card_id[card_id] = AccessState(
                revoked_after_grant=True,
                revoked_date=str(row["access_date"]),
            )
            continue

        if access_status in _REVOKED_STATUSES:
            access_state_by_card_id[card_id] = current_state

    return access_state_by_card_id


def derive_workflow_status(
    lifecycle_state: str,
    admission_state: AdmissionState,
    access_state: AccessState,
) -> str:
    """Повертає текст статусу картки для відображення в таблиці."""

    # Порядок умов принциповий: незворотні стани життєвого циклу мають пріоритет
    # над похідними підказками з історії допусків і доступів.
    if lifecycle_state == "destroyed":
        return "знищено"
    if lifecycle_state == "sent":
        return "відправлено"
    if admission_state.revoked_after_grant and admission_state.revoked_date:
        destruction_date = shift_date(admission_state.revoked_date, years=5)
        return f"на знищення\nДата знищення:\n{destruction_date}"
    if access_state.revoked_after_grant and access_state.revoked_date:
        cancellation_date = shift_date(access_state.revoked_date, months=6)
        return f"на скасування\nДата скасування:\n{cancellation_date}"
    if admission_state.has_active and access_state.has_active and admission_state.reissue_date:
        return f"переоформлення\nДата переоформлення:\n{admission_state.reissue_date}"
    return ""


def shift_date(value: str, years: int = 0, months: int = 0) -> str:
    """Зсуває дату на задану кількість років або місяців із корекцією кінця місяця."""

    parsed_date = datetime.strptime(value, "%d.%m.%Y").date()
    target_year = parsed_date.year + years
    target_month = parsed_date.month + months

    while target_month > 12:
        target_year += 1
        target_month -= 12

    while target_month < 1:
        target_year -= 1
        target_month += 12

    day = parsed_date.day
    while True:
        try:
            shifted_date = date(target_year, target_month, day)
            return shifted_date.strftime("%d.%m.%Y")
        except ValueError:
            day -= 1


def _sort_key_from_date(value: str) -> tuple[int, datetime]:
    # Порожні або некоректні дати спеціально йдуть у кінець,
    # щоб не ламати хронологію валідних записів.
    if not value:
        return (1, datetime.min)

    try:
        return (0, datetime.strptime(value, "%d.%m.%Y"))
    except ValueError:
        return (1, datetime.min)


def _admission_form_level(value: str) -> int | None:
    # Підтримуємо і кириличний, і латинський префікс форми,
    # бо в різних джерелах дані можуть приходити в обох варіантах.
    normalized_value = value.strip().upper().replace("Ф", "F")
    if normalized_value in {"F-1", "F-2", "F-3"}:
        return int(normalized_value[-1])
    return None


def _build_reissue_date(active_sequence: list[tuple[int, str]]) -> str:
    if not active_sequence:
        return ""

    current_level, current_date = active_sequence[-1]
    duration_years = {1: 5, 2: 7, 3: 10}.get(current_level)
    if duration_years is None:
        return ""

    # Для вищої форми беремо точку відліку з попередньої безперервної форми.
    base_date = current_date
    if current_level == 2:
        for form_level, grant_date in active_sequence:
            if form_level == 1:
                base_date = grant_date
                break
    elif current_level == 3:
        for form_level, grant_date in active_sequence:
            if form_level == 2:
                base_date = grant_date
                break

    return shift_date(base_date, years=duration_years)
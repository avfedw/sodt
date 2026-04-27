"""Експорт довідок 14 у Word за шаблоном."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile


_WORD_NAMESPACE = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_XMLNS_NAMESPACE = "http://www.w3.org/2000/xmlns/"
_XML_NAMESPACES = {"w": _WORD_NAMESPACE}
_TEMPLATE_NAME = "Довідка Ф-14-Шаблон.dotx"
_CONTENT_TYPES_PATH = "[Content_Types].xml"
_DOCUMENT_XML_PATH = "word/document.xml"
_SEPARATOR_MARKER = "-----"
_SECOND_CERTIFICATE_MARKER = "Підлягає поверненню до СОДТ в/ч А3783"
_UKRAINIAN_MONTHS = {
    1: "січня",
    2: "лютого",
    3: "березня",
    4: "квітня",
    5: "травня",
    6: "червня",
    7: "липня",
    8: "серпня",
    9: "вересня",
    10: "жовтня",
    11: "листопада",
    12: "грудня",
}
_TEMPLATE_NAMESPACES = {
    "wpc": "http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas",
    "cx": "http://schemas.microsoft.com/office/drawing/2014/chartex",
    "cx1": "http://schemas.microsoft.com/office/drawing/2015/9/8/chartex",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "o": "urn:schemas-microsoft-com:office:office",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "v": "urn:schemas-microsoft-com:vml",
    "wp14": "http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "w10": "urn:schemas-microsoft-com:office:word",
    "w": _WORD_NAMESPACE,
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
    "w15": "http://schemas.microsoft.com/office/word/2012/wordml",
    "w16se": "http://schemas.microsoft.com/office/word/2015/wordml/symex",
    "wpg": "http://schemas.microsoft.com/office/word/2010/wordprocessingGroup",
    "wpi": "http://schemas.microsoft.com/office/word/2010/wordprocessingInk",
    "wne": "http://schemas.microsoft.com/office/word/2006/wordml",
    "wps": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
}

for _prefix, _namespace_uri in _TEMPLATE_NAMESPACES.items():
    ET.register_namespace(_prefix, _namespace_uri)


@dataclass(slots=True)
class Certificate14ExportData:
    """Дані однієї довідки для підстановки у шаблон."""

    full_name: str
    order_day: str
    order_month: str
    order_year: str
    order_number: str
    admission_form: str
    expiration_year: str
    certificate_date: str
    certificate_number: str


def export_certificate14_documents(
    records: list[Certificate14ExportData],
    destination_path: str | Path,
    template_path: str | Path | None = None,
) -> Path:
    """Створює документ Word з довідками 14 за шаблоном."""

    if not records:
        raise ValueError("Потрібно вибрати хоча б одну довідку для експорту.")

    resolved_template_path = Path(template_path) if template_path is not None else _default_template_path()
    if not resolved_template_path.exists():
        raise ValueError("Шаблон довідки 14 не знайдено.")

    destination = Path(destination_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    with ZipFile(resolved_template_path) as template_archive:
        archive_entries = {
            name: template_archive.read(name)
            for name in template_archive.namelist()
        }

    document_root = ET.fromstring(archive_entries[_DOCUMENT_XML_PATH])
    _ensure_template_namespaces(document_root)
    _rebuild_document_body(document_root, records)
    _prune_empty_text_nodes(document_root)
    document_xml_bytes = ET.tostring(document_root, encoding="utf-8", xml_declaration=True)
    document_xml_bytes = _ensure_required_namespace_declarations(document_xml_bytes)
    archive_entries[_DOCUMENT_XML_PATH] = document_xml_bytes
    archive_entries[_CONTENT_TYPES_PATH] = _convert_template_content_types_to_document(archive_entries[_CONTENT_TYPES_PATH])

    with ZipFile(destination, "w", compression=ZIP_DEFLATED) as output_archive:
        for name, data in archive_entries.items():
            output_archive.writestr(name, data)

    return destination


def build_export_data(
    full_name: str,
    certificate_number: str,
    certificate_date: str,
    expiration_date: str,
    admission_form: str,
    order_number: str,
    order_date: str,
) -> Certificate14ExportData:
    """Готує значення полів для однієї довідки."""

    order_day, order_month, order_year = _split_date_for_order(order_date)
    expiration_year = _extract_year(expiration_date)
    return Certificate14ExportData(
        full_name=_to_dative_full_name(full_name),
        order_day=order_day,
        order_month=order_month,
        order_year=order_year,
        order_number=order_number.strip(),
        admission_form=admission_form.strip(),
        expiration_year=expiration_year,
        certificate_date=certificate_date.strip(),
        certificate_number=certificate_number.strip(),
    )


def _default_template_path() -> Path:
    return Path(__file__).resolve().parents[1] / _TEMPLATE_NAME


def _ensure_template_namespaces(document_root: ET.Element) -> None:
    for prefix, namespace_uri in _TEMPLATE_NAMESPACES.items():
        document_root.set(f"{{{_XMLNS_NAMESPACE}}}{prefix}", namespace_uri)


def _ensure_required_namespace_declarations(document_xml_bytes: bytes) -> bytes:
    document_xml = document_xml_bytes.decode("utf-8")
    insertion = ""
    for prefix, namespace_uri in _TEMPLATE_NAMESPACES.items():
        declaration = f'xmlns:{prefix}="{namespace_uri}"'
        if declaration not in document_xml:
            insertion += f" {declaration}"

    if insertion:
        document_xml = document_xml.replace("<w:document ", f"<w:document{insertion} ", 1)

    return document_xml.encode("utf-8")


def _prune_empty_text_nodes(document_root: ET.Element) -> None:
    for parent in document_root.iter():
        text_nodes = [child for child in list(parent) if child.tag == _tag("t") and not (child.text or "")]
        for child in text_nodes:
            parent.remove(child)


def _rebuild_document_body(document_root: ET.Element, records: list[Certificate14ExportData]) -> None:
    body = document_root.find("w:body", _XML_NAMESPACES)
    if body is None:
        raise ValueError("У шаблоні довідки 14 не знайдено тіло документа.")

    body_children = list(body)
    sect_pr = body_children[-1] if body_children and body_children[-1].tag == _tag("sectPr") else None
    content_children = body_children[:-1] if sect_pr is not None else body_children

    separator_index = _find_separator_index(content_children)
    second_start_index = _find_second_certificate_start(content_children, separator_index)
    if separator_index is None or second_start_index is None:
        raise ValueError("Не вдалося визначити межі довідок у шаблоні 14.")

    top_block = content_children[:separator_index]
    separator_block = content_children[separator_index:second_start_index]
    bottom_block = content_children[second_start_index:]

    rebuilt_children: list[ET.Element] = []
    for page_index, page_records in enumerate(_chunk_records(records, size=2)):
        if page_index > 0:
            rebuilt_children.append(_build_page_break_paragraph())

        rebuilt_children.extend(_fill_certificate_block(top_block, page_records[0]))
        if len(page_records) > 1:
            rebuilt_children.extend(deepcopy(element) for element in separator_block)
            rebuilt_children.extend(_fill_certificate_block(bottom_block, page_records[1]))

    body[:] = rebuilt_children + ([deepcopy(sect_pr)] if sect_pr is not None else [])


def _find_separator_index(elements: list[ET.Element]) -> int | None:
    for index, element in enumerate(elements):
        if _plain_text(element).count("-") >= len(_SEPARATOR_MARKER):
            return index
    return None


def _find_second_certificate_start(elements: list[ET.Element], separator_index: int | None) -> int | None:
    if separator_index is None:
        return None
    for index in range(separator_index + 1, len(elements)):
        if _SECOND_CERTIFICATE_MARKER in _plain_text(elements[index]):
            return index
    return None


def _fill_certificate_block(elements: list[ET.Element], record: Certificate14ExportData) -> list[ET.Element]:
    placeholders = {
        "ПРІЗВИЩЕ Ім’я По батькові": record.full_name,
        "число": record.order_day,
        "місяць": record.order_month,
        "рік": record.order_year,
        "номер": record.order_number,
        "форма": record.admission_form,
        "рік дійсна": record.expiration_year,
        "дата довідки": record.certificate_date,
        "номер довідки": record.certificate_number,
    }

    filled_elements: list[ET.Element] = []
    for source_element in elements:
        element = deepcopy(source_element)
        _replace_placeholders_in_element(element, placeholders)
        filled_elements.append(element)
    return filled_elements


def _replace_placeholders_in_element(element: ET.Element, placeholders: dict[str, str]) -> None:
    text_nodes = list(element.findall(".//w:t", _XML_NAMESPACES))
    for index in range(len(text_nodes) - 2):
        left_node = text_nodes[index]
        middle_node = text_nodes[index + 1]
        right_node = text_nodes[index + 2]
        if (left_node.text or "") != "{" or (right_node.text or "") != "}":
            continue
        placeholder_name = (middle_node.text or "").strip()
        if placeholder_name not in placeholders:
            continue
        left_node.text = ""
        middle_node.text = placeholders[placeholder_name]
        right_node.text = ""


def _convert_template_content_types_to_document(content_types_bytes: bytes) -> bytes:
    content_text = content_types_bytes.decode("utf-8")
    content_text = content_text.replace(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.template.main+xml",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml",
    )
    return content_text.encode("utf-8")


def _split_date_for_order(value: str) -> tuple[str, str, str]:
    normalized_value = value.strip()
    if not normalized_value:
        return "", "", ""
    try:
        parsed = datetime.strptime(normalized_value, "%d.%m.%Y")
    except ValueError:
        return "", "", ""
    return str(parsed.day), _UKRAINIAN_MONTHS[parsed.month], str(parsed.year)


def _extract_year(value: str) -> str:
    normalized_value = value.strip()
    if not normalized_value:
        return ""
    try:
        return str(datetime.strptime(normalized_value, "%d.%m.%Y").year)
    except ValueError:
        return ""


def _to_dative_full_name(full_name: str) -> str:
    parts = [part for part in full_name.strip().split() if part]
    if len(parts) != 3:
        return full_name.strip()

    surname, name, patronymic = parts
    is_female = _looks_like_female_patronymic(patronymic)
    return " ".join(
        (
            _to_dative_surname(surname, is_female=is_female),
            _to_dative_given_name(name, is_female=is_female),
            _to_dative_patronymic(patronymic, is_female=is_female),
        )
    )


def _looks_like_female_patronymic(value: str) -> bool:
    normalized_value = value.casefold()
    return normalized_value.endswith(("івна", "ївна", "овна", "евна", "євна"))


def _to_dative_patronymic(value: str, is_female: bool) -> str:
    if not value:
        return value
    if is_female:
        for suffix in ("івна", "ївна", "овна", "евна", "євна"):
            if value.casefold().endswith(suffix):
                return value[:-1] + "і"
        if value.casefold().endswith("на"):
            return value[:-1] + "і"
        return value
    if value.casefold().endswith("ич"):
        return value + "у"
    return _to_dative_given_name(value, is_female=False)


def _to_dative_given_name(value: str, is_female: bool) -> str:
    if not value:
        return value
    normalized_value = value.casefold()
    if normalized_value.endswith("ій"):
        return value[:-2] + "ію"
    if normalized_value.endswith("й"):
        return value[:-1] + "ю"
    if normalized_value.endswith("ь"):
        return value[:-1] + "ю"
    if normalized_value.endswith("о"):
        return value[:-1] + "ові"
    if normalized_value.endswith("а"):
        return value[:-1] + "і"
    if normalized_value.endswith("я"):
        return value[:-1] + ("ї" if is_female else "ю")
    if normalized_value.endswith(("р", "н", "м", "в", "г", "к", "п", "т", "д", "б", "з", "с", "ц", "ч", "ш", "щ", "ж", "л", "х", "ф")):
        return value + "у"
    return value


def _to_dative_surname(value: str, is_female: bool) -> str:
    if not value:
        return value
    normalized_value = value.casefold()
    if is_female:
        if normalized_value.endswith("а"):
            return value[:-1] + "і"
        if normalized_value.endswith("я"):
            return value[:-1] + "ї"
        return value
    if normalized_value.endswith("ій"):
        return value[:-2] + "ію"
    if normalized_value.endswith(("ь", "й")):
        return value[:-1] + "ю"
    if normalized_value.endswith("а"):
        return value[:-1] + "і"
    if normalized_value.endswith("я"):
        return value[:-1] + "ю"
    if normalized_value.endswith(("енко", "ко")):
        return value[:-1] + "у"
    if normalized_value.endswith(("ук", "юк", "чук", "чак", "ак", "ик", "ок")):
        return value + "у"
    if normalized_value.endswith(("ов", "ев", "єв", "ін", "ин", "ський", "зький", "цький")):
        return value + "у"
    if normalized_value.endswith(("р", "н", "м", "в", "г", "к", "п", "т", "д", "б", "з", "с", "ц", "ч", "ш", "щ", "ж", "л", "х", "ф")):
        return value + "у"
    return value


def _chunk_records(records: list[Certificate14ExportData], size: int) -> list[list[Certificate14ExportData]]:
    return [records[index:index + size] for index in range(0, len(records), size)]


def _build_page_break_paragraph() -> ET.Element:
    paragraph = ET.Element(_tag("p"))
    run = ET.SubElement(paragraph, _tag("r"))
    break_node = ET.SubElement(run, _tag("br"))
    break_node.set(_tag("type"), "page")
    return paragraph


def _plain_text(element: ET.Element) -> str:
    return "".join(node.text or "" for node in element.findall(".//w:t", _XML_NAMESPACES))


def _tag(local_name: str) -> str:
    return f"{{{_WORD_NAMESPACE}}}{local_name}"
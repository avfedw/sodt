"""Пакет доступу до бази даних застосунку."""

# Експортуємо лише основний репозиторій і його моделі,
# щоб решта коду не тягнула внутрішні допоміжні модулі напряму.
from .cards_repository import CardRecord, CardsRepository
from .nomenclature_repository import AssignmentHistoryRecord, NomenclatureRecord, NomenclatureRepository
from .structure_repository import StructureRepository, StructureUnitRecord

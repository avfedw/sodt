# Project Guidelines

## Code Style
- This is a small Python desktop application built with PySide6.
- Keep changes minimal and consistent with the existing straightforward style.
- Write all code comments and docstrings in Ukrainian.
- Prefer explicit, readable Python over abstractions that do not simplify this codebase.

## Architecture
- Entry point: `main.py` creates `QApplication` and opens `views.main_window.MainWindow`.
- Follow the existing separation of responsibilities:
  - `views/` contains PySide6 widgets and window composition.
  - `viewmodels/` contains UI-facing logic and coordinates data access.
  - `dialogs/` contains modal dialog classes and shared dialog behavior.
  - `db/` contains SQLite access and validation logic.
  - `locales/` contains localized UI strings.
- Keep database operations inside repository classes instead of embedding SQL in views.
- When working around import cycles between UI and localization layers, prefer the existing lazy-import pattern used in `viewmodels/tab_cards_vm.py`.

## Build and Test
- Install dependencies with `pip install -r requirements.txt`.
- Run the application with `python main.py` from the workspace root.
- There is currently no automated test suite configured. If you add behavior that can be validated narrowly, prefer a focused check or a small new test over broad manual-only verification.

## Conventions
- The project uses an MVVM-like structure for the cards tab. Extend the existing layer boundaries instead of bypassing them.
- SQLite data for the app lives in `db/sodt.sqlite3`. Preserve schema compatibility unless the task explicitly requires a migration.
- Repository methods may normalize and validate Ukrainian-language input before saving. Keep validation close to the repository when extending card persistence behavior.
- `db/cards_repository.py` uses `CardRecord` as the table row model. Reuse that pattern for card-related data flow.
- `locales/` is the source of UI text. Prefer adding new labels there instead of hardcoding strings in views or dialogs.
- The `export/` directory exists but does not currently define an implemented workflow. Do not assume export functionality is already wired.
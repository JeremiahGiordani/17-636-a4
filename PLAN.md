# Build Plan — Minimal Spreadsheet (Base System)

## File Layout

```
app.py                  # Flask application (routes + cell state)
engine.py               # Formula engine (parse, evaluate, dependency graph)
templates/index.html    # Single-page frontend
static/style.css        # Grid styling
static/app.js           # Frontend JS (cell editing, API calls)
tests/
  conftest.py           # Pytest fixtures (Flask test client, engine helpers)
  test_engine.py        # Formula engine unit tests (acceptance tests 1-16)
  test_api.py           # Flask endpoint tests via test client
requirements.txt        # flask, pytest
```

## Shared Interfaces

### Formula Engine (`engine.py`)

```python
class Spreadsheet:
    """Holds all cell state and evaluates formulas."""

    def set_cell(self, cell_id: str, raw: str) -> dict:
        """Set a cell's raw content and recalculate.

        Args:
            cell_id: e.g. "A1", "J10" (case-insensitive)
            raw: literal number string, formula string starting with '=', or ""

        Returns:
            dict of every cell whose value changed, keyed by uppercase cell id:
            {
                "A1": {"raw": "=B1+1", "value": 6},
                "B1": {"raw": "5",     "value": 5},
            }
            If a cell has an error, value is None and "error" key is present:
            {"A1": {"raw": "=1/0", "value": None, "error": "division by zero"}}
        """

    def get_all_cells(self) -> dict:
        """Return the full grid state.

        Returns:
            dict keyed by cell id for every cell that has been set:
            {"A1": {"raw": "5", "value": 5}, ...}
        """
```

### Flask Endpoints (`app.py`)

| Method | Path     | Request Body                     | Response (200)                              |
|--------|----------|----------------------------------|---------------------------------------------|
| GET    | `/`      | —                                | Rendered `templates/index.html`             |
| GET    | `/cells` | —                                | `{"cells": {<cell_id>: {raw, value, ?error}, ...}}` |
| POST   | `/cells` | `{"cell": "A1", "raw": "=B1+1"}` | `{"cells": {<changed cells>}}`              |

POST `/cells` returns **400** if cell identifier is invalid or out of range.

## Build Tasks (ordered)

1. **engine.py — parsing & evaluation**: Implement formula tokenizer/parser
   with operator precedence, cell references, unary minus, parentheses.
2. **engine.py — Spreadsheet class**: Cell storage, dependency graph,
   topological recalculation, circular-reference detection, error propagation.
3. **app.py — Flask routes**: GET `/`, GET `/cells`, POST `/cells` wired to
   the `Spreadsheet` instance.
4. **Frontend**: `templates/index.html`, `static/style.css`, `static/app.js` —
   10×10 editable grid, POST on edit, render results.
5. **Integration & polish**: Run full test suite, fix failures, verify in browser.

## Definition of Done

The pytest suite in `tests/` encodes all 16 acceptance tests from SPEC.md.
**The build stage must make the code pass the test suite without weakening or
deleting any tests.** All tests passing = done.

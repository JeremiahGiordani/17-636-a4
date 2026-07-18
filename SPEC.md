# Minimal Spreadsheet — Specification

## Overview

A browser-based spreadsheet application with a 10×10 grid of editable cells.
Each cell holds either a literal numeric value or a formula (prefixed with `=`)
that can reference other cells and use basic arithmetic. The Python/Flask backend
evaluates all formulas and detects errors (division by zero, invalid expressions,
circular references). The frontend is a single-page vanilla HTML/CSS/JS grid
that sends cell updates to the backend and renders the computed results.

## In Scope (Base System)

- A fixed 10×10 grid (columns A–J, rows 1–10).
- Cells hold either a **literal value** (numeric, e.g. `42`, `3.14`, `-7`) or a
  **formula** starting with `=` (e.g. `=A1+B2*3`).
- Formulas support the four arithmetic operators `+`, `-`, `*`, `/` and
  parentheses for grouping.
- Formulas may contain **cell references** like `A1`, `J10` (column letter +
  row number). References are case-insensitive.
- When a cell is edited, the backend **recalculates** every cell that depends on
  it (directly or transitively).
- The Flask backend evaluates formulas; the frontend never evaluates them.

## Out of Scope (Deferred to Extension)

- Built-in functions (`SUM`, `AVG`, `IF`, etc.).
- Range references (`A1:A5`).
- Saving/loading sheets (SQLite persistence).
- Cell styling, formatting, or conditional formatting.
- Multiple sheets/tabs.
- Non-numeric literal values (strings, dates).
- Collaborative/multi-user editing.

## Tech Stack

| Layer    | Technology                  |
|----------|-----------------------------|
| Backend  | Python 3, Flask             |
| Frontend | Vanilla HTML, CSS, JS       |
| Tests    | pytest                      |

No database in the base system. All cell state lives in server memory.

## Backend API

### `GET /`

Serves the frontend HTML page.

### `GET /cells`

Returns the full grid state.

**Response** `200 OK`
```json
{
  "cells": {
    "A1": { "raw": "=B1+1", "value": 6 },
    "B1": { "raw": "5",     "value": 5 },
    "C1": { "raw": "",      "value": 0 }
  }
}
```

- `raw`: the literal or formula string the user entered (empty string if never
  edited).
- `value`: the computed numeric result, or `null` if the cell has an error.
- Only cells that have been edited or are affected by edits need to appear;
  unmentioned cells are implicitly empty (value `0`).
- If a cell is in an error state, an `error` field is included:
  ```json
  { "raw": "=1/0", "value": null, "error": "division by zero" }
  ```

### `POST /cells`

Sets one cell's raw content and triggers recalculation.

**Request**
```json
{
  "cell": "A1",
  "raw": "=B1+1"
}
```

**Response** `200 OK`
```json
{
  "cells": {
    "A1": { "raw": "=B1+1", "value": 6 },
    "D1": { "raw": "=A1*2", "value": 12 }
  }
}
```

The response returns the updated cell **and** every other cell whose value
changed as a result of the recalculation.

**Error responses:**
- `400` if the cell identifier is invalid or out of range.

## Formula Evaluation Rules

1. **Literal values**: A cell containing a plain number (e.g. `42`) evaluates to
   that number. A cell that is empty evaluates to `0`.
2. **Formula parsing**: A formula starts with `=` followed by an arithmetic
   expression. The expression may contain decimal literals, cell references,
   `+`, `-`, `*`, `/`, and parentheses. Unary minus is supported (e.g. `=-A1`).
3. **Cell references**: `A1` through `J10`. Case-insensitive. A reference to an
   **empty or never-edited cell** evaluates to `0`.
4. **Operator precedence**: Standard arithmetic — `*` and `/` bind tighter than
   `+` and `-`. Parentheses override precedence.
5. **Division by zero**: Produces an error. The cell's `value` is `null` and an
   `error` string is returned.
6. **Invalid formula**: Any formula that cannot be parsed (e.g. `=A1++`,
   `=hello`) produces an error.
7. **Circular references**: If setting a cell would create a dependency cycle
   (e.g. A1=`=B1`, B1=`=A1`), the backend detects this and returns an error for
   every cell in the cycle. The backend must never enter an infinite loop.
8. **Error propagation**: A cell that references a cell in an error state is
   itself in an error state.

## Acceptance Tests

The following cases will become pytest tests. Each describes cell inputs and the
expected computed output.

| #  | Category              | Setup                                      | Expected Result                          |
|----|-----------------------|--------------------------------------------|------------------------------------------|
| 1  | Literal value         | Set A1 = `5`                               | A1 value = 5                             |
| 2  | Simple addition       | A1 = `2`, B1 = `3`, C1 = `=A1+B1`         | C1 value = 5                             |
| 3  | Operator precedence   | A1 = `2`, B1 = `3`, C1 = `4`, D1 = `=A1+B1*C1` | D1 value = 14  (not 20)            |
| 4  | Parentheses           | A1 = `2`, B1 = `3`, C1 = `4`, D1 = `=(A1+B1)*C1` | D1 value = 20                    |
| 5  | Division              | A1 = `10`, B1 = `4`, C1 = `=A1/B1`        | C1 value = 2.5                           |
| 6  | Cell reference chain  | A1 = `1`, B1 = `=A1+1`, C1 = `=B1+1`      | B1 = 2, C1 = 3                          |
| 7  | Recalculation         | A1 = `1`, B1 = `=A1*10`; then update A1 = `5` | B1 value = 50                        |
| 8  | Empty cell ref        | A1 = `=B1+1` (B1 never set)               | A1 value = 1  (empty cell = 0)           |
| 9  | Division by zero      | A1 = `1`, B1 = `0`, C1 = `=A1/B1`         | C1 has error `"division by zero"`        |
| 10 | Invalid formula       | A1 = `=2++3`                               | A1 has error                             |
| 11 | Circular reference    | A1 = `=B1`, B1 = `=A1`                    | Both A1 and B1 have a circular-ref error |
| 12 | Self-reference        | A1 = `=A1+1`                               | A1 has error (circular)                  |
| 13 | Error propagation     | A1 = `=1/0`, B1 = `=A1+1`                 | Both A1 and B1 have errors               |
| 14 | Negative literal      | A1 = `-3`, B1 = `=A1*2`                   | A1 = -3, B1 = -6                         |
| 15 | Unary minus in formula| A1 = `5`, B1 = `=-A1`                     | B1 = -5                                  |
| 16 | Decimal values        | A1 = `3.14`, B1 = `=A1*2`                 | B1 = 6.28                                |

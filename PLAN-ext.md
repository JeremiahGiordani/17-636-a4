# Build Plan — Extension (Functions & Ranges)

## What Changes

Only `engine.py` changes. `app.py`, templates, and existing tests stay untouched.

## Engine Changes (engine.py)

### 1. Tokenizer

Add new token types to `_TOKEN_RE` / `_tokenize`:
- **Colon** `:` — range separator
- **Comma** `,` — argument separator
- **Comparison operators** `>=`, `<=`, `<>`, `>`, `<`, `=` (multi-char first)
- **Function names** `SUM`, `AVG`, `MIN`, `MAX`, `COUNT`, `IF` (case-insensitive)

Token types become: `NUM`, `CELL`, `OP`, `FUNC`, `COLON`, `COMMA`, `CMP`.

### 2. Parser

Extend the grammar:

```
expr   → cmp_expr
cmp_expr → add_expr (CMP add_expr)?      # at most one comparison
add_expr → term (('+' | '-') term)*
term   → unary (('*' | '/') unary)*
unary  → '-' unary | atom
atom   → NUM | CELL | FUNC '(' arglist ')' | '(' expr ')'
arglist → arg (',' arg)*
arg     → range | expr
range   → CELL ':' CELL
```

New AST nodes:
- `('cmp', op, left, right)` — comparison
- `('func', name, [args...])` — function call
- `('range', start_cell, end_cell)` — cell range (only valid inside func args)

Validation at parse time:
- Range outside a function → parse error
- `SUM/AVG/MIN/MAX/COUNT` with 0 args → parse error
- `IF` without exactly 3 args → parse error
- Range endpoints must be valid cells (A-J, 1-10)

### 3. Reference Collection (`_collect_refs`)

Handle new node types:
- `'func'` → recurse into each argument
- `'range'` → expand to all cells in the rectangle, add each
- `'cmp'` → recurse into both sides

### 4. Evaluation (`_eval_ast`)

New cases:

- **`cmp`**: Evaluate both sides, apply comparison, return `1` or `0`.
- **`range`**: Expand the range to a list of `(cell_id, value, is_empty)` tuples.
  Check each cell for errors (propagate). Return the list for the enclosing
  function to consume.
- **`func`**: Collect argument values (ranges expand to multiple values,
  non-ranges produce a single value). Then:
  - **SUM**: sum all numeric values
  - **AVG**: mean of non-empty values; error if none
  - **MIN**: min of all values (empty = 0)
  - **MAX**: max of all values (empty = 0)
  - **COUNT**: count of non-empty cells (literals always count)
  - **IF**: evaluate condition; if truthy evaluate & return arg 2, else arg 3.
    Lazy — only evaluate the selected branch.

For IF lazy evaluation, the function node must receive unevaluated AST branches
and evaluate the selected one on demand, rather than pre-evaluating all args.

### 5. Empty-Cell Tracking

The `Spreadsheet` class already tracks which cells have been set via `_raw`.
During range expansion, a cell is "empty" if it has no entry in `_raw` or its
raw value is `""`. This distinction matters for AVG (exclude empty from
denominator) and COUNT (don't count empty).

## Files Changed

| File | Change |
|------|--------|
| `engine.py` | Tokenizer, parser, ref-collection, evaluator extended |
| `tests/test_functions.py` | New test file (acceptance tests 17-44) |
| `PLAN-ext.md` | This plan |

`app.py`, `templates/`, `static/`, `tests/test_engine.py`, `tests/test_api.py`,
`tests/conftest.py` — **no changes**.

## Task Breakdown (ordered)

1. **Tokenizer**: Add `:`, `,`, comparison operators, and function-name tokens.
2. **Parser**: Extend grammar for function calls, ranges, comparisons, arglist.
   Add parse-time validation (arg counts, range-only-in-function, valid
   endpoints).
3. **`_collect_refs`**: Handle `func`, `range`, `cmp` AST nodes.
4. **Evaluator**: Implement `cmp`, `range` expansion, and all six functions
   (SUM, AVG, MIN, MAX, COUNT, IF) with correct empty-cell semantics and lazy
   eval for IF.
5. **Run full test suite**: All 44 tests (16 base + 28 extension) must pass with
   no tests weakened or deleted.

## Definition of Done

The complete pytest suite (`tests/test_engine.py` + `tests/test_api.py` +
`tests/test_functions.py`) passes. No existing tests are modified or weakened.

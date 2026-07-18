# progress.md

The loop's shared memory. The agent updates this file each iteration so the
next run knows what is done and what is left. Populated during the build stages.

## Status
- [x] base system
- [x] extension

## Base System — Complete

All 27 tests pass (16 engine tests, 11 API tests).

### What was built
- [x] `engine.py` — Formula engine: tokenizer, recursive-descent parser,
  AST evaluator, Spreadsheet class with dependency tracking, topological
  recalculation, circular reference detection, error propagation
- [x] `app.py` — Flask routes: GET /, GET /cells, POST /cells with validation
- [x] `templates/index.html` — Single-page HTML with 10x10 grid
- [x] `static/style.css` — Grid styling
- [x] `static/app.js` — Frontend JS: cell editing, API calls, result rendering

## Extension — Complete

All 55 tests pass (27 base + 28 extension).

### What was built
- [x] Tokenizer: FUNC, CMP, COLON, COMMA token types; case-insensitive function names
- [x] Parser: function calls with arglist, ranges (CELL:CELL), comparison operators
- [x] Range expansion: rectangular A1:C3 ranges, reversed ranges normalized
- [x] Aggregate functions: SUM, AVG, MIN, MAX, COUNT with correct empty-cell semantics
- [x] IF function: 3-arg conditional with lazy evaluation (error in unused branch ignored)
- [x] Comparison operators: >, <, >=, <=, =, <> yielding 1/0
- [x] Nesting: functions in arithmetic, functions as args to functions, functions in IF conditions
- [x] Error handling: parse errors for bare ranges, empty args, wrong IF arg count; error propagation through ranges

### What remains
Nothing — all features complete, all tests passing.

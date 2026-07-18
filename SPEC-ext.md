# Extension Specification — Spreadsheet Functions & Ranges

## Overview

This extension adds range references (`A1:C3`) and built-in functions
(`SUM`, `AVG`, `MIN`, `MAX`, `COUNT`, `IF`) to the formula engine. Functions
accept ranges and/or individual cell/literal arguments, may nest inside other
functions and combine with arithmetic, and propagate errors from any argument.
The base system (API endpoints, request/response shapes, existing formula
syntax) remains fully backward compatible; all 27 existing tests continue to
pass unchanged.

## Range References

A **range** is written as two cell references separated by a colon —
`<top-left>:<bottom-right>` — and denotes the rectangular block of cells
between (and including) both corners.

- **Parsing**: A range `X1:Y2` expands to every cell `(col, row)` where
  `col` runs from `X` to `Y` and `row` runs from `1` to `2`. Column and row
  order in the two corners may be swapped (e.g. `B3:A1` is equivalent to
  `A1:B3`); the engine normalizes to top-left / bottom-right.
- **Expansion example**: `A1:C3` expands to the 9 cells
  `A1 A2 A3 B1 B2 B3 C1 C2 C3`.
- **Validity**: Both endpoints must be valid cell identifiers (`A`–`J`,
  `1`–`10`). An invalid endpoint (e.g. `Z1:A1`) is a parse error.
- **Usage restriction**: Ranges may only appear as arguments to functions.
  Using a range outside a function (e.g. `=A1:A3+1`) is a parse error.

## Aggregate Functions — SUM, AVG, MIN, MAX, COUNT

Each aggregate function accepts one or more arguments separated by commas.
An argument is either a range, a cell reference, or a numeric literal
(including expressions like `1+2` in argument position).

| Function | Semantics |
|----------|-----------|
| `SUM`    | Returns the sum of all numeric values. |
| `AVG`    | Returns the arithmetic mean of all numeric values. |
| `MIN`    | Returns the smallest numeric value. |
| `MAX`    | Returns the largest numeric value. |
| `COUNT`  | Returns the count of non-empty cells (cells that have been set to a non-empty raw value). Literal arguments always count as 1. |

### Empty-cell handling

An **empty cell** is one that has never been set or whose raw content is `""`.
Its numeric value is `0` (unchanged from the base system).

- **SUM, MIN, MAX**: Empty cells contribute their value of `0` normally.
  `SUM(A1:A3)` where only `A1=5` → `5 + 0 + 0 = 5`.
  `MIN(A1:A3)` where only `A1=5` → `0` (empty cells count as 0).
- **AVG**: Empty cells are **excluded** from both the numerator and the
  denominator. `AVG(A1:A3)` where only `A1=6` → `6 / 1 = 6`, not `6 / 3`.
  If every cell in the range is empty, `AVG` returns an error
  (`"no values to average"`).
- **COUNT**: Empty cells are **not counted**. `COUNT(A1:A3)` where only
  `A1=5` → `1`.

### Error handling

- If **any** cell in a range (or any argument) is in an error state, the
  function returns an error (error propagation, same as base-system rule 8).
- Zero arguments to an aggregate (e.g. `SUM()`) is a parse error.
- `AVG` of a selection with no non-empty cells → error `"no values to average"`.

## IF Function

```
IF(condition, value_if_true, value_if_false)
```

- **condition**: An expression using a comparison operator. Supported
  comparison operators: `>`, `<`, `>=`, `<=`, `=`, `<>` (not equal).
- The condition evaluates to `1` (true) or `0` (false).
- If the condition is true (non-zero), the result is `value_if_true`;
  otherwise `value_if_false`.
- `value_if_true` and `value_if_false` are arbitrary expressions (may contain
  cell references, arithmetic, nested function calls).
- **Lazy evaluation**: Only the selected branch is evaluated. If the
  non-selected branch contains an error, the formula does NOT produce an
  error. (The condition itself is always evaluated.)
- `IF` requires exactly 3 arguments. Fewer or more is a parse error.

### Comparison operators

| Operator | Meaning           |
|----------|-------------------|
| `>`      | greater than      |
| `<`      | less than         |
| `>=`     | greater or equal  |
| `<=`     | less or equal     |
| `=`      | equal             |
| `<>`     | not equal         |

Comparisons operate on numeric values. The comparison itself yields `1`
(true) or `0` (false) and may appear only as the first argument to `IF`.

## Nesting and Combining with Arithmetic

Functions return a single numeric value and may appear anywhere an atom can:

- `=SUM(A1:A3)*2` — function result used in arithmetic.
- `=IF(SUM(A1:A2)>5, 100, 0)` — function nested inside IF condition.
- `=SUM(A1:A3) + MAX(B1:B3)` — multiple functions in one formula.
- `=SUM(A1, SUM(B1:B3))` — function as an argument to another function.

## Backward Compatibility

- All existing API endpoints and response shapes are unchanged.
- Existing formulas (arithmetic, cell references, literals) parse and
  evaluate identically.
- All 27 existing tests pass without modification.

## Acceptance Tests

The tests below use the same `sheet` fixture as the base tests. Cell setup
is noted in the **Setup** column; the last `set_cell` call (or `get_all_cells`)
produces the **Expected** result. Tests are numbered starting at 17 to
continue from the base suite.

| #  | Category | Setup | Expected |
|----|----------|-------|----------|
| 17 | SUM over range | A1=`1`, A2=`2`, A3=`3`; set D1=`=SUM(A1:A3)` | D1 value = 6 |
| 18 | SUM with mixed args | A1=`10`, B1=`20`; set C1=`=SUM(A1, B1, 5)` | C1 value = 35 |
| 19 | AVG over range | A1=`10`, A2=`20`, A3=`30`; set D1=`=AVG(A1:A3)` | D1 value = 20 |
| 20 | AVG skips empty cells | A1=`6`, A2 never set, A3=`12`; set D1=`=AVG(A1:A3)` | D1 value = 9 (mean of 6 and 12; A2 excluded) |
| 21 | AVG all empty → error | A1, A2, A3 all never set; set D1=`=AVG(A1:A3)` | D1 has error |
| 22 | MIN over range | A1=`5`, A2=`-3`, A3=`10`; set D1=`=MIN(A1:A3)` | D1 value = -3 |
| 23 | MAX over range | A1=`5`, A2=`-3`, A3=`10`; set D1=`=MAX(A1:A3)` | D1 value = 10 |
| 24 | COUNT non-empty cells | A1=`7`, A2 never set, A3=`0`; set D1=`=COUNT(A1:A3)` | D1 value = 2 (A1 and A3 set; A2 never set) |
| 25 | COUNT all empty | A1, A2, A3 never set; set D1=`=COUNT(A1:A3)` | D1 value = 0 |
| 26 | Range across columns | A1=`1`, B1=`2`, A2=`3`, B2=`4`; set C1=`=SUM(A1:B2)` | C1 value = 10 |
| 27 | Reversed range | A1=`1`, A2=`2`, A3=`3`; set D1=`=SUM(A3:A1)` | D1 value = 6 (same as A1:A3) |
| 28 | IF true branch | A1=`10`; set B1=`=IF(A1>5, 1, 0)` | B1 value = 1 |
| 29 | IF false branch | A1=`3`; set B1=`=IF(A1>5, 1, 0)` | B1 value = 0 |
| 30 | IF with `=` operator | A1=`7`; set B1=`=IF(A1=7, 100, 200)` | B1 value = 100 |
| 31 | IF with `<>` operator | A1=`7`; set B1=`=IF(A1<>7, 100, 200)` | B1 value = 200 |
| 32 | IF with `<` operator | A1=`3`; set B1=`=IF(A1<5, 10, 20)` | B1 value = 10 |
| 33 | IF with `>=` operator | A1=`5`; set B1=`=IF(A1>=5, 10, 20)` | B1 value = 10 |
| 34 | IF with `<=` operator | A1=`5`; set B1=`=IF(A1<=5, 10, 20)` | B1 value = 10 |
| 35 | IF lazy eval — error in unused branch | A1=`10`, B1=`=1/0`; set C1=`=IF(A1>5, 99, B1)` | C1 value = 99 (B1 error ignored) |
| 36 | Nested function in IF condition | A1=`3`, A2=`4`; set B1=`=IF(SUM(A1:A2)>5, 100, 0)` | B1 value = 100 |
| 37 | Function result in arithmetic | A1=`1`, A2=`2`, A3=`3`; set D1=`=SUM(A1:A3)*2` | D1 value = 12 |
| 38 | Multiple functions in formula | A1=`5`, B1=`10`; set C1=`=MIN(A1,B1)+MAX(A1,B1)` | C1 value = 15 |
| 39 | Nested function call | A1=`1`, B1=`2`, B2=`3`; set C1=`=SUM(A1, SUM(B1:B2))` | C1 value = 6 |
| 40 | Error propagation in range | A1=`=1/0`, A2=`5`; set B1=`=SUM(A1:A2)` | B1 has error |
| 41 | SUM empty cells contribute 0 | A1=`5`, A2 never set; set B1=`=SUM(A1:A2)` | B1 value = 5 |
| 42 | Range as invalid bare expression | set A1=`=A1:A3+1` | A1 has error (parse error) |
| 43 | SUM no args → error | set A1=`=SUM()` | A1 has error (parse error) |
| 44 | IF wrong arg count | set A1=`=IF(1>0, 1)` | A1 has error (parse error) |

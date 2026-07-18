"""Extension acceptance tests — functions, ranges, IF (SPEC-ext.md tests 17-44)."""

import pytest


# ── Test 17: SUM over range ────────────────────────────────────────────
def test_sum_over_range(sheet):
    sheet.set_cell("A1", "1")
    sheet.set_cell("A2", "2")
    sheet.set_cell("A3", "3")
    result = sheet.set_cell("D1", "=SUM(A1:A3)")
    assert result["D1"]["value"] == 6


# ── Test 18: SUM with mixed args ──────────────────────────────────────
def test_sum_mixed_args(sheet):
    sheet.set_cell("A1", "10")
    sheet.set_cell("B1", "20")
    result = sheet.set_cell("C1", "=SUM(A1, B1, 5)")
    assert result["C1"]["value"] == 35


# ── Test 19: AVG over range ───────────────────────────────────────────
def test_avg_over_range(sheet):
    sheet.set_cell("A1", "10")
    sheet.set_cell("A2", "20")
    sheet.set_cell("A3", "30")
    result = sheet.set_cell("D1", "=AVG(A1:A3)")
    assert result["D1"]["value"] == 20


# ── Test 20: AVG skips empty cells ────────────────────────────────────
def test_avg_skips_empty(sheet):
    sheet.set_cell("A1", "6")
    # A2 never set
    sheet.set_cell("A3", "12")
    result = sheet.set_cell("D1", "=AVG(A1:A3)")
    assert result["D1"]["value"] == 9  # mean of 6 and 12; A2 excluded


# ── Test 21: AVG all empty → error ────────────────────────────────────
def test_avg_all_empty_error(sheet):
    # A1, A2, A3 never set
    result = sheet.set_cell("D1", "=AVG(A1:A3)")
    assert result["D1"]["value"] is None
    assert "error" in result["D1"]


# ── Test 22: MIN over range ───────────────────────────────────────────
def test_min_over_range(sheet):
    sheet.set_cell("A1", "5")
    sheet.set_cell("A2", "-3")
    sheet.set_cell("A3", "10")
    result = sheet.set_cell("D1", "=MIN(A1:A3)")
    assert result["D1"]["value"] == -3


# ── Test 23: MAX over range ───────────────────────────────────────────
def test_max_over_range(sheet):
    sheet.set_cell("A1", "5")
    sheet.set_cell("A2", "-3")
    sheet.set_cell("A3", "10")
    result = sheet.set_cell("D1", "=MAX(A1:A3)")
    assert result["D1"]["value"] == 10


# ── Test 24: COUNT non-empty cells ────────────────────────────────────
def test_count_non_empty(sheet):
    sheet.set_cell("A1", "7")
    # A2 never set
    sheet.set_cell("A3", "0")
    result = sheet.set_cell("D1", "=COUNT(A1:A3)")
    assert result["D1"]["value"] == 2  # A1 and A3 set; A2 never set


# ── Test 25: COUNT all empty ──────────────────────────────────────────
def test_count_all_empty(sheet):
    # A1, A2, A3 never set
    result = sheet.set_cell("D1", "=COUNT(A1:A3)")
    assert result["D1"]["value"] == 0


# ── Test 26: Range across columns ─────────────────────────────────────
def test_range_across_columns(sheet):
    sheet.set_cell("A1", "1")
    sheet.set_cell("B1", "2")
    sheet.set_cell("A2", "3")
    sheet.set_cell("B2", "4")
    result = sheet.set_cell("C1", "=SUM(A1:B2)")
    assert result["C1"]["value"] == 10


# ── Test 27: Reversed range ───────────────────────────────────────────
def test_reversed_range(sheet):
    sheet.set_cell("A1", "1")
    sheet.set_cell("A2", "2")
    sheet.set_cell("A3", "3")
    result = sheet.set_cell("D1", "=SUM(A3:A1)")
    assert result["D1"]["value"] == 6  # same as A1:A3


# ── Test 28: IF true branch ───────────────────────────────────────────
def test_if_true_branch(sheet):
    sheet.set_cell("A1", "10")
    result = sheet.set_cell("B1", "=IF(A1>5, 1, 0)")
    assert result["B1"]["value"] == 1


# ── Test 29: IF false branch ──────────────────────────────────────────
def test_if_false_branch(sheet):
    sheet.set_cell("A1", "3")
    result = sheet.set_cell("B1", "=IF(A1>5, 1, 0)")
    assert result["B1"]["value"] == 0


# ── Test 30: IF with = operator ───────────────────────────────────────
def test_if_equal(sheet):
    sheet.set_cell("A1", "7")
    result = sheet.set_cell("B1", "=IF(A1=7, 100, 200)")
    assert result["B1"]["value"] == 100


# ── Test 31: IF with <> operator ──────────────────────────────────────
def test_if_not_equal(sheet):
    sheet.set_cell("A1", "7")
    result = sheet.set_cell("B1", "=IF(A1<>7, 100, 200)")
    assert result["B1"]["value"] == 200


# ── Test 32: IF with < operator ───────────────────────────────────────
def test_if_less_than(sheet):
    sheet.set_cell("A1", "3")
    result = sheet.set_cell("B1", "=IF(A1<5, 10, 20)")
    assert result["B1"]["value"] == 10


# ── Test 33: IF with >= operator ──────────────────────────────────────
def test_if_greater_equal(sheet):
    sheet.set_cell("A1", "5")
    result = sheet.set_cell("B1", "=IF(A1>=5, 10, 20)")
    assert result["B1"]["value"] == 10


# ── Test 34: IF with <= operator ──────────────────────────────────────
def test_if_less_equal(sheet):
    sheet.set_cell("A1", "5")
    result = sheet.set_cell("B1", "=IF(A1<=5, 10, 20)")
    assert result["B1"]["value"] == 10


# ── Test 35: IF lazy eval — error in unused branch ────────────────────
def test_if_lazy_eval(sheet):
    sheet.set_cell("A1", "10")
    sheet.set_cell("B1", "=1/0")
    result = sheet.set_cell("C1", "=IF(A1>5, 99, B1)")
    assert result["C1"]["value"] == 99  # B1 error ignored


# ── Test 36: Nested function in IF condition ──────────────────────────
def test_nested_function_in_if_condition(sheet):
    sheet.set_cell("A1", "3")
    sheet.set_cell("A2", "4")
    result = sheet.set_cell("B1", "=IF(SUM(A1:A2)>5, 100, 0)")
    assert result["B1"]["value"] == 100


# ── Test 37: Function result in arithmetic ────────────────────────────
def test_function_in_arithmetic(sheet):
    sheet.set_cell("A1", "1")
    sheet.set_cell("A2", "2")
    sheet.set_cell("A3", "3")
    result = sheet.set_cell("D1", "=SUM(A1:A3)*2")
    assert result["D1"]["value"] == 12


# ── Test 38: Multiple functions in formula ────────────────────────────
def test_multiple_functions(sheet):
    sheet.set_cell("A1", "5")
    sheet.set_cell("B1", "10")
    result = sheet.set_cell("C1", "=MIN(A1,B1)+MAX(A1,B1)")
    assert result["C1"]["value"] == 15


# ── Test 39: Nested function call ─────────────────────────────────────
def test_nested_function_call(sheet):
    sheet.set_cell("A1", "1")
    sheet.set_cell("B1", "2")
    sheet.set_cell("B2", "3")
    result = sheet.set_cell("C1", "=SUM(A1, SUM(B1:B2))")
    assert result["C1"]["value"] == 6


# ── Test 40: Error propagation in range ───────────────────────────────
def test_error_propagation_in_range(sheet):
    sheet.set_cell("A1", "=1/0")
    sheet.set_cell("A2", "5")
    result = sheet.set_cell("B1", "=SUM(A1:A2)")
    assert result["B1"]["value"] is None
    assert "error" in result["B1"]


# ── Test 41: SUM empty cells contribute 0 ─────────────────────────────
def test_sum_empty_cells(sheet):
    sheet.set_cell("A1", "5")
    # A2 never set
    result = sheet.set_cell("B1", "=SUM(A1:A2)")
    assert result["B1"]["value"] == 5


# ── Test 42: Range as invalid bare expression ─────────────────────────
def test_range_bare_expression_error(sheet):
    result = sheet.set_cell("A1", "=A1:A3+1")
    assert result["A1"]["value"] is None
    assert "error" in result["A1"]


# ── Test 43: SUM no args → error ──────────────────────────────────────
def test_sum_no_args_error(sheet):
    result = sheet.set_cell("A1", "=SUM()")
    assert result["A1"]["value"] is None
    assert "error" in result["A1"]


# ── Test 44: IF wrong arg count ───────────────────────────────────────
def test_if_wrong_arg_count(sheet):
    result = sheet.set_cell("A1", "=IF(1>0, 1)")
    assert result["A1"]["value"] is None
    assert "error" in result["A1"]

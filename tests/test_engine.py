"""Engine-level acceptance tests (SPEC.md tests 1-16)."""

import pytest


# ── Test 1: Literal value ───────────────────────────────────────────
def test_literal_value(sheet):
    result = sheet.set_cell("A1", "5")
    assert result["A1"]["value"] == 5


# ── Test 2: Simple addition ─────────────────────────────────────────
def test_simple_addition(sheet):
    sheet.set_cell("A1", "2")
    sheet.set_cell("B1", "3")
    result = sheet.set_cell("C1", "=A1+B1")
    assert result["C1"]["value"] == 5


# ── Test 3: Operator precedence ─────────────────────────────────────
def test_operator_precedence(sheet):
    sheet.set_cell("A1", "2")
    sheet.set_cell("B1", "3")
    sheet.set_cell("C1", "4")
    result = sheet.set_cell("D1", "=A1+B1*C1")
    assert result["D1"]["value"] == 14  # not 20


# ── Test 4: Parentheses ─────────────────────────────────────────────
def test_parentheses(sheet):
    sheet.set_cell("A1", "2")
    sheet.set_cell("B1", "3")
    sheet.set_cell("C1", "4")
    result = sheet.set_cell("D1", "=(A1+B1)*C1")
    assert result["D1"]["value"] == 20


# ── Test 5: Division ────────────────────────────────────────────────
def test_division(sheet):
    sheet.set_cell("A1", "10")
    sheet.set_cell("B1", "4")
    result = sheet.set_cell("C1", "=A1/B1")
    assert result["C1"]["value"] == 2.5


# ── Test 6: Cell reference chain ────────────────────────────────────
def test_cell_reference_chain(sheet):
    sheet.set_cell("A1", "1")
    sheet.set_cell("B1", "=A1+1")
    result = sheet.set_cell("C1", "=B1+1")
    assert result["C1"]["value"] == 3
    # Also verify B1 was computed correctly
    all_cells = sheet.get_all_cells()
    assert all_cells["B1"]["value"] == 2


# ── Test 7: Recalculation ───────────────────────────────────────────
def test_recalculation(sheet):
    sheet.set_cell("A1", "1")
    sheet.set_cell("B1", "=A1*10")
    all_cells = sheet.get_all_cells()
    assert all_cells["B1"]["value"] == 10
    # Update A1 — B1 should recalculate
    result = sheet.set_cell("A1", "5")
    assert result["B1"]["value"] == 50


# ── Test 8: Empty cell reference ────────────────────────────────────
def test_empty_cell_reference(sheet):
    result = sheet.set_cell("A1", "=B1+1")
    assert result["A1"]["value"] == 1  # B1 never set → 0


# ── Test 9: Division by zero ────────────────────────────────────────
def test_division_by_zero(sheet):
    sheet.set_cell("A1", "1")
    sheet.set_cell("B1", "0")
    result = sheet.set_cell("C1", "=A1/B1")
    assert result["C1"]["value"] is None
    assert "error" in result["C1"]


# ── Test 10: Invalid formula ────────────────────────────────────────
def test_invalid_formula(sheet):
    result = sheet.set_cell("A1", "=2++3")
    assert result["A1"]["value"] is None
    assert "error" in result["A1"]


# ── Test 11: Circular reference ─────────────────────────────────────
def test_circular_reference(sheet):
    sheet.set_cell("A1", "=B1")
    result = sheet.set_cell("B1", "=A1")
    assert result["A1"]["value"] is None
    assert "error" in result["A1"]
    assert result["B1"]["value"] is None
    assert "error" in result["B1"]


# ── Test 12: Self-reference ─────────────────────────────────────────
def test_self_reference(sheet):
    result = sheet.set_cell("A1", "=A1+1")
    assert result["A1"]["value"] is None
    assert "error" in result["A1"]


# ── Test 13: Error propagation ──────────────────────────────────────
def test_error_propagation(sheet):
    sheet.set_cell("A1", "=1/0")
    result = sheet.set_cell("B1", "=A1+1")
    assert result["B1"]["value"] is None
    assert "error" in result["B1"]
    # A1 should also still be in error
    all_cells = sheet.get_all_cells()
    assert all_cells["A1"]["value"] is None
    assert "error" in all_cells["A1"]


# ── Test 14: Negative literal ───────────────────────────────────────
def test_negative_literal(sheet):
    sheet.set_cell("A1", "-3")
    result = sheet.set_cell("B1", "=A1*2")
    assert result["B1"]["value"] == -6
    all_cells = sheet.get_all_cells()
    assert all_cells["A1"]["value"] == -3


# ── Test 15: Unary minus in formula ─────────────────────────────────
def test_unary_minus_in_formula(sheet):
    sheet.set_cell("A1", "5")
    result = sheet.set_cell("B1", "=-A1")
    assert result["B1"]["value"] == -5


# ── Test 16: Decimal values ─────────────────────────────────────────
def test_decimal_values(sheet):
    sheet.set_cell("A1", "3.14")
    result = sheet.set_cell("B1", "=A1*2")
    assert result["B1"]["value"] == pytest.approx(6.28)

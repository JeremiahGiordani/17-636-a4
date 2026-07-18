"""Flask endpoint acceptance tests (SPEC.md tests via HTTP API)."""

import json
import pytest


def post_cell(client, cell, raw):
    """Helper: POST a cell update and return parsed JSON."""
    resp = client.post(
        "/cells",
        data=json.dumps({"cell": cell, "raw": raw}),
        content_type="application/json",
    )
    return resp


# ── GET / serves the frontend ───────────────────────────────────────
def test_get_index(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"<" in resp.data  # contains HTML


# ── GET /cells returns grid state ───────────────────────────────────
def test_get_cells_empty(client):
    resp = client.get("/cells")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "cells" in data


# ── POST /cells with invalid cell id returns 400 ────────────────────
def test_post_invalid_cell(client):
    resp = post_cell(client, "Z99", "5")
    assert resp.status_code == 400


def test_post_missing_cell_field(client):
    resp = client.post(
        "/cells",
        data=json.dumps({"raw": "5"}),
        content_type="application/json",
    )
    assert resp.status_code == 400


# ── Test 1 (API): Literal value ─────────────────────────────────────
def test_api_literal_value(client):
    resp = post_cell(client, "A1", "5")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["cells"]["A1"]["value"] == 5


# ── Test 2 (API): Simple addition ───────────────────────────────────
def test_api_simple_addition(client):
    post_cell(client, "A1", "2")
    post_cell(client, "B1", "3")
    resp = post_cell(client, "C1", "=A1+B1")
    data = resp.get_json()
    assert data["cells"]["C1"]["value"] == 5


# ── Test 7 (API): Recalculation ─────────────────────────────────────
def test_api_recalculation(client):
    post_cell(client, "A1", "1")
    post_cell(client, "B1", "=A1*10")
    resp = post_cell(client, "A1", "5")
    data = resp.get_json()
    # B1 should be in the response as a changed cell
    assert data["cells"]["B1"]["value"] == 50


# ── Test 9 (API): Division by zero ──────────────────────────────────
def test_api_division_by_zero(client):
    post_cell(client, "A1", "1")
    post_cell(client, "B1", "0")
    resp = post_cell(client, "C1", "=A1/B1")
    data = resp.get_json()
    assert data["cells"]["C1"]["value"] is None
    assert "error" in data["cells"]["C1"]


# ── Test 11 (API): Circular reference ───────────────────────────────
def test_api_circular_reference(client):
    post_cell(client, "A1", "=B1")
    resp = post_cell(client, "B1", "=A1")
    data = resp.get_json()
    assert data["cells"]["A1"]["value"] is None
    assert "error" in data["cells"]["A1"]
    assert data["cells"]["B1"]["value"] is None
    assert "error" in data["cells"]["B1"]


# ── Test 13 (API): Error propagation ────────────────────────────────
def test_api_error_propagation(client):
    post_cell(client, "A1", "=1/0")
    resp = post_cell(client, "B1", "=A1+1")
    data = resp.get_json()
    assert data["cells"]["B1"]["value"] is None
    assert "error" in data["cells"]["B1"]


# ── GET /cells reflects all state ───────────────────────────────────
def test_get_cells_after_edits(client):
    post_cell(client, "A1", "10")
    post_cell(client, "B1", "=A1+5")
    resp = client.get("/cells")
    data = resp.get_json()
    assert data["cells"]["A1"]["value"] == 10
    assert data["cells"]["B1"]["value"] == 15

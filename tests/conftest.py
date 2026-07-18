"""Shared pytest fixtures for the spreadsheet test suite."""

import sys
import os

# Ensure repo root is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from engine import Spreadsheet
from app import app as flask_app


@pytest.fixture
def sheet():
    """Fresh Spreadsheet instance for engine tests."""
    return Spreadsheet()


@pytest.fixture
def client():
    """Flask test client with a fresh app state per test."""
    flask_app.config["TESTING"] = True
    # Reset the spreadsheet state between tests
    from app import reset_state
    reset_state()
    with flask_app.test_client() as c:
        yield c

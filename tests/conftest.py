"""Pytest configuration and fixtures"""
import pytest
import sys
sys.path.insert(0, '.')

from test_helpers import (
    create_test_pokemon,
    create_test_deck,
    create_test_players,
    create_test_battle_engine
)

@pytest.fixture
def basic_pokemon():
    """Fixture for a basic test Pokemon"""
    return create_test_pokemon()

@pytest.fixture
def test_deck():
    """Fixture for a test deck"""
    return create_test_deck(20)

@pytest.fixture
def test_players():
    """Fixture for two test players"""
    return create_test_players()

@pytest.fixture
def battle_engine():
    """Fixture for a test battle engine"""
    return create_test_battle_engine()


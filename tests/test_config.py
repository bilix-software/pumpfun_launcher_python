"""Tests for TokenConfig."""

import pytest
from pump_fun_launcher import TokenConfig

def test_valid_config():
    """Test valid configuration."""
    config = TokenConfig(
        name="Test Token",
        symbol="TEST",
        metadata_url="https://example.com/metadata.json"
    )
    assert config.validate()

def test_empty_name():
    """Test empty name validation."""
    with pytest.raises(ValueError, match="Token name is required"):
        TokenConfig(
            name="",
            symbol="TEST", 
            metadata_url="https://example.com/metadata.json"
        )

def test_empty_symbol():
    """Test empty symbol validation."""
    with pytest.raises(ValueError, match="Token symbol is required"):
        TokenConfig(
            name="Test Token",
            symbol="",
            metadata_url="https://example.com/metadata.json"
        )

def test_long_symbol():
    """Test symbol length validation."""
    with pytest.raises(ValueError, match="Token symbol must be 10 characters or less"):
        TokenConfig(
            name="Test Token",
            symbol="VERYLONGSYMBOL",
            metadata_url="https://example.com/metadata.json"
        )

def test_negative_initial_buy():
    """Test negative initial buy validation."""
    with pytest.raises(ValueError, match="Initial buy amount must be non-negative"):
        TokenConfig(
            name="Test Token",
            symbol="TEST",
            metadata_url="https://example.com/metadata.json",
            initial_buy=-0.1
        )

def test_negative_priority_fee():
    """Test negative priority fee validation."""
    with pytest.raises(ValueError, match="Priority fee must be non-negative"):
        TokenConfig(
            name="Test Token",
            symbol="TEST", 
            metadata_url="https://example.com/metadata.json",
            priority_fee=-0.001
        )
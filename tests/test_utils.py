"""Tests for utility functions."""

import pytest
from solders.keypair import Keypair
from pump_fun_launcher.utils import (
    get_keypair_from_private_key,
    create_string_buffer,
    calculate_buy_amounts
)

def test_create_string_buffer():
    """Test string buffer creation."""
    result = create_string_buffer("hello")
    expected = b'\x05\x00\x00\x00hello'
    assert result == expected

def test_calculate_buy_amounts():
    """Test buy amount calculations."""
    sol_amount = 0.001
    sol_lamports, token_out, max_cost = calculate_buy_amounts(sol_amount, 5.0)
    
    assert sol_lamports == 1_000_000  # 0.001 SOL in lamports
    assert token_out > 0
    assert max_cost > sol_lamports  # Should include slippage

def test_get_keypair_from_private_key_invalid():
    """Test invalid private key handling."""
    with pytest.raises(ValueError, match="Invalid private key format"):
        get_keypair_from_private_key("invalid_key")

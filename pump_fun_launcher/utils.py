"""Utility functions for the pump.fun token launcher."""

import base64
from typing import Union
from solders.keypair import Keypair
from solders.pubkey import Pubkey

def get_keypair_from_private_key(private_key: str) -> Keypair:
    """
    Convert a private key string to a Keypair object.
    
    Args:
        private_key: Base58 or base64 encoded private key
        
    Returns:
        Keypair object
        
    Raises:
        ValueError: If the private key format is invalid
    """
    try:
        # Try base58 first (most common format)
        return Keypair.from_base58_string(private_key)
    except Exception:
        try:
            # Try base64
            decoded = base64.b64decode(private_key)
            return Keypair.from_bytes(decoded)
        except Exception as e:
            raise ValueError(f"Invalid private key format. Must be base58 or base64 encoded: {e}")

def create_string_buffer(s: str) -> bytes:
    """Create a length-prefixed string buffer for Solana instructions."""
    encoded = s.encode('utf-8')
    return len(encoded).to_bytes(4, 'little') + encoded

def calculate_buy_amounts(initial_buy_sol: float, slippage: float = 5.0) -> tuple[int, int, int]:
    """
    Calculate buy amounts for the bonding curve.
    
    Args:
        initial_buy_sol: Amount of SOL to spend
        slippage: Slippage tolerance in percentage (default 5%)
        
    Returns:
        Tuple of (sol_in_lamports, token_out, max_sol_cost)
    """
    from .constants import LAMPORTS_PER_SOL, VIRTUAL_TOKEN_RESERVES, VIRTUAL_SOL_RESERVES
    
    sol_in_lamports = int(initial_buy_sol * LAMPORTS_PER_SOL)
    
    # Bonding curve calculation
    product = VIRTUAL_SOL_RESERVES * VIRTUAL_TOKEN_RESERVES
    new_virtual_sol_reserves = VIRTUAL_SOL_RESERVES + sol_in_lamports
    new_virtual_token_reserves = product // new_virtual_sol_reserves + 1
    token_out = VIRTUAL_TOKEN_RESERVES - new_virtual_token_reserves
    token_out = min(token_out, VIRTUAL_TOKEN_RESERVES)
    
    # Calculate max cost with slippage
    sol_in_with_slippage = initial_buy_sol * (1 + slippage / 100)
    max_sol_cost = int(sol_in_with_slippage * LAMPORTS_PER_SOL)
    
    return sol_in_lamports, token_out, max_sol_cost

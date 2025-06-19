# pump_fun_launcher/__init__.py
"""
Pump.Fun Token Launcher

A Python package for programmatically launching tokens on pump.fun.
"""

from .launcher import launch_token
from .config import TokenConfig
from .types import LaunchResult
from .utils import get_keypair_from_private_key
from .constants import *

__version__ = "1.0.0"
__author__ = "Bilix Software"
__email__ = "info@bilix.io"

__all__ = [
    "launch_token",
    "TokenConfig", 
    "LaunchResult",
    "get_keypair_from_private_key",
    # Constants
    "GLOBAL",
    "PUMP_FUN_PROGRAM",
    "PUMP_FUN_ACCOUNT",
    "MPL_TOKEN_METADATA",
    "MINT_AUTHORITY",
    "TOKEN_PROGRAM_ID",
    "ASSOCIATED_TOKEN_PROGRAM_ID",
    "SYSTEM_PROGRAM_ID",
    "RENT",
]

# pump_fun_launcher/constants.py
"""Constants for pump.fun token launcher."""

from solders.pubkey import Pubkey
from solders.system_program import ID as SYSTEM_PROGRAM_ID
from solders.sysvar import RENT

# Program IDs and important addresses
GLOBAL = Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf")
PUMP_FUN_PROGRAM = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
PUMP_FUN_ACCOUNT = Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1")
MPL_TOKEN_METADATA = Pubkey.from_string("metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s")
MINT_AUTHORITY = Pubkey.from_string("TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM")

# Token program addresses
TOKEN_PROGRAM_ID = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ASSOCIATED_TOKEN_PROGRAM_ID = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")

# System constants
LAMPORTS_PER_SOL = 1_000_000_000
VIRTUAL_TOKEN_RESERVES = 1073000000000000
VIRTUAL_SOL_RESERVES = 30000000000

# Default values
DEFAULT_INITIAL_BUY = 0.01
DEFAULT_PRIORITY_FEE = 0.001
DEFAULT_SLIPPAGE = 5.0

# pump_fun_launcher/types.py
"""Type definitions for the pump.fun token launcher."""

from dataclasses import dataclass
from typing import Optional

@dataclass
class LaunchResult:
    """Result of a token launch operation."""
    success: bool
    signature: Optional[str] = None
    token_address: Optional[str] = None
    error: Optional[str] = None

    def __str__(self) -> str:
        if self.success:
            return f"✅ Success: Token {self.token_address} | Signature: {self.signature}"
        else:
            return f"❌ Failed: {self.error}"

# pump_fun_launcher/config.py
"""Configuration classes for token launches."""

from dataclasses import dataclass
from typing import Optional
from solders.keypair import Keypair
from .constants import DEFAULT_INITIAL_BUY, DEFAULT_PRIORITY_FEE

@dataclass
class TokenConfig:
    """Configuration for launching a token on pump.fun."""
    name: str
    symbol: str
    metadata_url: str
    initial_buy: float = DEFAULT_INITIAL_BUY
    priority_fee: float = DEFAULT_PRIORITY_FEE
    mint_keypair: Optional[Keypair] = None

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.name or not self.name.strip():
            raise ValueError("Token name is required and cannot be empty")
        
        if not self.symbol or not self.symbol.strip():
            raise ValueError("Token symbol is required and cannot be empty")
        
        if len(self.symbol) > 10:
            raise ValueError("Token symbol must be 10 characters or less")
        
        if not self.metadata_url or not self.metadata_url.strip():
            raise ValueError("Metadata URL is required and cannot be empty")
        
        if self.initial_buy < 0:
            raise ValueError("Initial buy amount must be non-negative")
        
        if self.priority_fee < 0:
            raise ValueError("Priority fee must be non-negative")

    def validate(self) -> bool:
        """Validate the configuration. Returns True if valid, raises ValueError if not."""
        # Validation is done in __post_init__, so if we reach here, it's valid
        return True

# pump_fun_launcher/utils.py
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

# pump_fun_launcher/instructions.py
"""Instruction builders for pump.fun operations."""

from typing import List
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.instruction import Instruction, AccountMeta
from solders.compute_budget import set_compute_unit_price, set_compute_unit_limit

from .config import TokenConfig
from .utils import create_string_buffer, calculate_buy_amounts
from .constants import (
    GLOBAL, MINT_AUTHORITY, MPL_TOKEN_METADATA, PUMP_FUN_ACCOUNT,
    PUMP_FUN_PROGRAM, TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID,
    SYSTEM_PROGRAM_ID, RENT, LAMPORTS_PER_SOL
)

def create_launch_instruction(
    config: TokenConfig,
    mint_keypair: Keypair,
    payer: Pubkey,
    bonding_curve: Pubkey,
    associated_bonding_curve: Pubkey,
    metadata: Pubkey
) -> Instruction:
    """Create the token launch instruction."""
    
    accounts = [
        AccountMeta(pubkey=mint_keypair.pubkey(), is_signer=True, is_writable=True),
        AccountMeta(pubkey=MINT_AUTHORITY, is_signer=False, is_writable=False),
        AccountMeta(pubkey=bonding_curve, is_signer=False, is_writable=True),
        AccountMeta(pubkey=associated_bonding_curve, is_signer=False, is_writable=True),
        AccountMeta(pubkey=GLOBAL, is_signer=False, is_writable=False),
        AccountMeta(pubkey=MPL_TOKEN_METADATA, is_signer=False, is_writable=False),
        AccountMeta(pubkey=metadata, is_signer=False, is_writable=True),
        AccountMeta(pubkey=payer, is_signer=True, is_writable=True),
        AccountMeta(pubkey=SYSTEM_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=ASSOCIATED_TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=RENT, is_signer=False, is_writable=False),
        AccountMeta(pubkey=PUMP_FUN_ACCOUNT, is_signer=False, is_writable=False),
        AccountMeta(pubkey=PUMP_FUN_PROGRAM, is_signer=False, is_writable=False),
    ]
    
    # Create instruction data
    instruction_code = bytes.fromhex("181ec828051c0777")
    name_buffer = create_string_buffer(config.name)
    symbol_buffer = create_string_buffer(config.symbol)
    uri_buffer = create_string_buffer(config.metadata_url)
    
    data = instruction_code + name_buffer + symbol_buffer + uri_buffer + bytes(payer)
    
    return Instruction(
        program_id=PUMP_FUN_PROGRAM,
        accounts=accounts,
        data=data
    )

def create_ata_instruction(payer: Pubkey, token_account: Pubkey, mint: Pubkey) -> Instruction:
    """Create associated token account instruction."""
    return Instruction(
        program_id=ASSOCIATED_TOKEN_PROGRAM_ID,
        accounts=[
            AccountMeta(pubkey=payer, is_signer=True, is_writable=True),
            AccountMeta(pubkey=token_account, is_signer=False, is_writable=True),
            AccountMeta(pubkey=payer, is_signer=False, is_writable=False),
            AccountMeta(pubkey=mint, is_signer=False, is_writable=False),
            AccountMeta(pubkey=SYSTEM_PROGRAM_ID, is_signer=False, is_writable=False),
            AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        ],
        data=b''
    )

def create_buy_instruction(
    mint: Pubkey,
    payer: Pubkey,
    token_account: Pubkey,
    bonding_curve: Pubkey,
    associated_bonding_curve: Pubkey,
    creator_vault: Pubkey,
    initial_buy: float,
    slippage: float = 5.0
) -> Instruction:
    """Create the buy instruction."""
    
    _, token_out, max_sol_cost = calculate_buy_amounts(initial_buy, slippage)
    
    accounts = [
        AccountMeta(pubkey=GLOBAL, is_signer=False, is_writable=False),
        AccountMeta(pubkey=Pubkey.from_string('G5UZAVbAf46s7cKWoyKu8kYTip9DGTpbLZ2qa9Aq69dP'), is_signer=False, is_writable=True),
        AccountMeta(pubkey=mint, is_signer=False, is_writable=False),
        AccountMeta(pubkey=bonding_curve, is_signer=False, is_writable=True),
        AccountMeta(pubkey=associated_bonding_curve, is_signer=False, is_writable=True),
        AccountMeta(pubkey=token_account, is_signer=False, is_writable=True),
        AccountMeta(pubkey=payer, is_signer=False, is_writable=True),
        AccountMeta(pubkey=SYSTEM_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=creator_vault, is_signer=False, is_writable=True),
        AccountMeta(pubkey=PUMP_FUN_ACCOUNT, is_signer=False, is_writable=False),
        AccountMeta(pubkey=PUMP_FUN_PROGRAM, is_signer=False, is_writable=False),
    ]
    
    # Create buy instruction data
    buy_instruction_code = int('16927863322537952870').to_bytes(8, 'little')
    token_out_bytes = token_out.to_bytes(8, 'little')
    max_sol_cost_bytes = max_sol_cost.to_bytes(8, 'little')
    
    data = buy_instruction_code + token_out_bytes + max_sol_cost_bytes
    
    return Instruction(
        program_id=PUMP_FUN_PROGRAM,
        accounts=accounts,
        data=data
    )

def create_priority_fee_instructions(priority_fee: float) -> List[Instruction]:
    """Create priority fee instructions."""
    if priority_fee <= 0:
        return []
    
    instructions = []
    
    # Set compute unit limit
    instructions.append(set_compute_unit_limit(300_000))
    
    # Set compute unit price
    micro_lamports = int((priority_fee / 3) * LAMPORTS_PER_SOL)
    instructions.append(set_compute_unit_price(micro_lamports))
    
    return instructions

# pump_fun_launcher/launcher.py
"""Main token launcher functionality."""

import asyncio
from typing import Union
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.message import MessageV0
from solders.transaction import VersionedTransaction
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TxOpts

from .config import TokenConfig
from .types import LaunchResult
from .utils import get_keypair_from_private_key
from .instructions import (
    create_launch_instruction,
    create_ata_instruction, 
    create_buy_instruction,
    create_priority_fee_instructions
)
from .constants import (
    PUMP_FUN_PROGRAM, TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID,
    MPL_TOKEN_METADATA
)

async def launch_token(
    config: TokenConfig,
    private_key: Union[str, Keypair],
    rpc_url: str = "https://api.mainnet-beta.solana.com"
) -> LaunchResult:
    """
    Launch a new token on pump.fun.
    
    Args:
        config: Token configuration
        private_key: Base58/base64 encoded private key or Keypair instance
        rpc_url: Solana RPC URL
        
    Returns:
        LaunchResult with success status and details
    """
    try:
        # Validate configuration
        config.validate()
        
        # Initialize client
        async with AsyncClient(rpc_url, commitment=Confirmed) as client:
            # Get keypair
            if isinstance(private_key, str):
                payer = get_keypair_from_private_key(private_key)
            else:
                payer = private_key
            
            # Use provided mint keypair or generate new one
            if config.mint_keypair:
                mint = config.mint_keypair
                print(f"Using provided mint keypair: {mint.pubkey()}")
            else:
                mint = Keypair()
                print(f"Generated new mint keypair: {mint.pubkey()}")
            
            print(f"Payer: {payer.pubkey()}")
            
            # Find program-derived addresses
            bonding_curve, _ = Pubkey.find_program_address(
                [b"bonding-curve", bytes(mint.pubkey())], 
                PUMP_FUN_PROGRAM
            )
            
            associated_bonding_curve, _ = Pubkey.find_program_address(
                [bytes(bonding_curve), bytes(TOKEN_PROGRAM_ID), bytes(mint.pubkey())],
                ASSOCIATED_TOKEN_PROGRAM_ID
            )
            
            metadata, _ = Pubkey.find_program_address(
                [b"metadata", bytes(MPL_TOKEN_METADATA), bytes(mint.pubkey())],
                MPL_TOKEN_METADATA
            )
            
            creator_vault, _ = Pubkey.find_program_address(
                [b"creator-vault", bytes(payer.pubkey())],
                PUMP_FUN_PROGRAM
            )
            
            # Build instructions
            instructions = []
            
            # Add priority fee instructions
            if config.priority_fee > 0:
                priority_instructions = create_priority_fee_instructions(config.priority_fee)
                instructions.extend(priority_instructions)
            
            # Add launch instruction
            launch_ix = create_launch_instruction(
                config, mint, payer.pubkey(), bonding_curve, 
                associated_bonding_curve, metadata
            )
            instructions.append(launch_ix)
            
            # Add buy instructions if initial buy > 0
            if config.initial_buy > 0:
                print(f"Adding initial buy of {config.initial_buy} SOL...")
                
                # Get associated token account
                token_account, _ = Pubkey.find_program_address(
                    [bytes(payer.pubkey()), bytes(TOKEN_PROGRAM_ID), bytes(mint.pubkey())],
                    ASSOCIATED_TOKEN_PROGRAM_ID
                )
                
                # Create ATA instruction
                ata_ix = create_ata_instruction(payer.pubkey(), token_account, mint.pubkey())
                instructions.append(ata_ix)
                
                # Create buy instruction
                buy_ix = create_buy_instruction(
                    mint.pubkey(), payer.pubkey(), token_account,
                    bonding_curve, associated_bonding_curve, creator_vault,
                    config.initial_buy
                )
                instructions.append(buy_ix)
            
            # Get latest blockhash
            blockhash_resp = await client.get_latest_blockhash()
            if not blockhash_resp.value:
                raise Exception("Failed to get blockhash")
            
            blockhash = blockhash_resp.value.blockhash
            
            # Create message
            message = MessageV0.try_compile(
                payer=payer.pubkey(),
                instructions=instructions,
                address_lookup_table_accounts=[],
                recent_blockhash=blockhash,
            )
            
            # Create and sign transaction
            transaction = VersionedTransaction(message, [payer, mint])
            
            # Send transaction
            opts = TxOpts(skip_preflight=True, preflight_commitment=Confirmed)
            response = await client.send_raw_transaction(
                txn=bytes(transaction),
                opts=opts
            )
            
            if not response.value:
                raise Exception("Transaction failed to send")
            
            signature = str(response.value)
            
            print(f"🎉 Token launched successfully!")
            print(f"Token Address: {mint.pubkey()}")
            print(f"Transaction: {signature}")
            
            if config.initial_buy > 0:
                print(f"✅ Initial buy of {config.initial_buy} SOL included!")
            
            return LaunchResult(
                success=True,
                signature=signature,
                token_address=str(mint.pubkey())
            )
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return LaunchResult(success=False, error=str(e))
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
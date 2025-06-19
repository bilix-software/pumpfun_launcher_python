#!/usr/bin/env python3
"""
Basic example of launching a token on pump.fun.
"""

import asyncio
import os
from pump_fun_launcher import launch_token, TokenConfig

async def main():
    """Basic token launch example."""
    # Create token configuration
    config = TokenConfig(
        name="My Test Token",
        symbol="MTT", 
        metadata_url="https://arweave.net/your-metadata-hash-here",
        initial_buy=0.001,  # 0.001 SOL
        priority_fee=0.0001  # 0.0001 SOL,
        # No mint_keypair - will auto-generate
    )
    
    # Get private key from environment variable
    private_key = os.getenv("SOLANA_PRIVATE_KEY")
    if not private_key:
        print("Please set SOLANA_PRIVATE_KEY environment variable")
        return
    
    print("Launching token...")
    result = await launch_token(config, private_key)
    
    if result.success:
        print(f"🎉 Success! Token: {result.token_address}")
        print(f"Transaction: {result.signature}")
        print(f"View on Pump.fun: https://pump.fun/{result.token_address}")
    else:
        print(f"❌ Failed: {result.error}")

if __name__ == "__main__":
    asyncio.run(main())

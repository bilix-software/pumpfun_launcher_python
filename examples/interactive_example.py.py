#!/usr/bin/env python3
"""
Interactive example for launching tokens with user input.
"""

import asyncio
import os
from solders.keypair import Keypair
from pump_fun_launcher import launch_token, TokenConfig

async def main():
    """Interactive token launcher."""
    print("🚀 Pump.Fun Token Launcher")
    print("=" * 40)
    
    # Get token details from user
    name = input("Token name: ").strip()
    symbol = input("Token symbol: ").strip().upper()
    metadata_url = input("Metadata URL: ").strip()
    
    try:
        initial_buy = float(input("Initial buy amount (SOL) [0.001]: ").strip() or "0.001")
        priority_fee = float(input("Priority fee (SOL) [0.0001]: ").strip() or "0.0001")
    except ValueError:
        print("Invalid number format, using defaults")
        initial_buy = 0.001
        priority_fee = 0.0001
    
    # Create configuration
    try:
        config = TokenConfig(
            name=name,
            symbol=symbol,
            metadata_url=metadata_url,
            initial_buy=initial_buy,
            priority_fee=priority_fee
        )
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return
    
    # Get private key
    private_key = os.getenv("SOLANA_PRIVATE_KEY")
    if not private_key:
        print("\n⚠️  No SOLANA_PRIVATE_KEY environment variable found")
        choice = input("Generate test keypair for devnet? (y/N): ").strip().lower()
        
        if choice == 'y':
            test_keypair = Keypair()
            private_key = test_keypair
            rpc_url = "https://api.devnet.solana.com"
            print(f"Generated test keypair: {test_keypair.pubkey()}")
            print("⚠️  You'll need devnet SOL to test")
        else:
            print("Please set SOLANA_PRIVATE_KEY environment variable")
            return
    else:
        rpc_url = "https://api.mainnet-beta.solana.com"
    
    # Confirm launch
    print(f"\n📋 Configuration:")
    print(f"  Name: {config.name}")
    print(f"  Symbol: {config.symbol}")
    print(f"  Initial Buy: {config.initial_buy} SOL")
    print(f"  Priority Fee: {config.priority_fee} SOL")
    print(f"  Estimated Cost: ~{config.initial_buy + config.priority_fee + 0.01} SOL")
    
    confirm = input(f"\n🚨 Launch token? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Launch cancelled")
        return
    
    # Launch token
    print("\n🚀 Launching token...")
    result = await launch_token(config, private_key, rpc_url)
    
    if result.success:
        print("\n" + "=" * 50)
        print("🎉 TOKEN LAUNCHED SUCCESSFULLY!")
        print("=" * 50)
        print(f"Token Address: {result.token_address}")
        print(f"Transaction: {result.signature}")
        
        if "devnet" in rpc_url:
            print(f"\n🔗 Devnet Links:")
            print(f"Token: https://solscan.io/token/{result.token_address}?cluster=devnet")
            print(f"Tx: https://solscan.io/tx/{result.signature}?cluster=devnet")
        else:
            print(f"\n🔗 Mainnet Links:")
            print(f"Token: https://solscan.io/token/{result.token_address}")
            print(f"Tx: https://solscan.io/tx/{result.signature}")
            print(f"Pump.fun: https://pump.fun/{result.token_address}")
    else:
        print(f"\n❌ Launch failed: {result.error}")

if __name__ == "__main__":
    asyncio.run(main())

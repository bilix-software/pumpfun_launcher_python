"""
Example showing how to use a custom mint keypair.
"""

import asyncio
import os
from solders.keypair import Keypair
from pump_fun_launcher import launch_token, TokenConfig

async def example_with_custom_mint():
    """Launch token with a custom mint keypair."""
    
    # Generate a custom mint keypair
    custom_mint = Keypair()
    print(f"Generated custom mint: {custom_mint.pubkey()}")
    
    # Create configuration with custom mint
    config = TokenConfig(
        name="Custom Mint Token",
        symbol="CMT",
        metadata_url="https://arweave.net/your-metadata-hash",
        initial_buy=0.001,
        priority_fee=0.0001,
        mint_keypair=custom_mint  # ← Custom mint keypair
    )
    
    private_key = os.getenv("SOLANA_PRIVATE_KEY")
    if not private_key:
        print("Please set SOLANA_PRIVATE_KEY environment variable")
        return
    
    print("Launching token with custom mint...")
    result = await launch_token(config, private_key)
    
    if result.success:
        print(f"🎉 Success!")
        print(f"Token Address: {result.token_address}")
        print(f"Custom mint used: {custom_mint.pubkey()}")
        print(f"Addresses match: {str(custom_mint.pubkey()) == result.token_address}")
    else:
        print(f"❌ Failed: {result.error}")

async def example_with_generated_mint():
    """Launch token with auto-generated mint keypair."""
    
    # Create configuration without mint_keypair (will be auto-generated)
    config = TokenConfig(
        name="Auto Generated Token",
        symbol="AGT", 
        metadata_url="https://arweave.net/your-metadata-hash",
        initial_buy=0.001,
        priority_fee=0.0001
        # No mint_keypair specified - will auto-generate
    )
    
    private_key = os.getenv("SOLANA_PRIVATE_KEY")
    if not private_key:
        print("Please set SOLANA_PRIVATE_KEY environment variable")
        return
    
    print("Launching token with auto-generated mint...")
    result = await launch_token(config, private_key)
    
    if result.success:
        print(f"🎉 Success!")
        print(f"Token Address: {result.token_address}")
        print("Mint was auto-generated")
    else:
        print(f"❌ Failed: {result.error}")

async def example_deterministic_mint():
    """Example of creating deterministic mint from seed."""
    
    # Create deterministic mint from a seed (for reproducible addresses)
    seed_phrase = "my-custom-token-seed-phrase"
    seed_bytes = seed_phrase.encode('utf-8')[:32]  # Take first 32 bytes
    seed_bytes = seed_bytes.ljust(32, b'\0')  # Pad to 32 bytes if needed
    
    deterministic_mint = Keypair.from_bytes(seed_bytes)
    print(f"Deterministic mint address: {deterministic_mint.pubkey()}")
    
    config = TokenConfig(
        name="Deterministic Token",
        symbol="DET",
        metadata_url="https://arweave.net/your-metadata-hash",
        initial_buy=0.001,
        priority_fee=0.0001,
        mint_keypair=deterministic_mint
    )
    
    private_key = os.getenv("SOLANA_PRIVATE_KEY")
    if not private_key:
        print("Please set SOLANA_PRIVATE_KEY environment variable")
        return
    
    print("Launching token with deterministic mint...")
    result = await launch_token(config, private_key)
    
    if result.success:
        print(f"🎉 Success!")
        print(f"Token Address: {result.token_address}")
        print("This address will always be the same for this seed!")
    else:
        print(f"❌ Failed: {result.error}")

async def main():
    """Run all examples."""
    print("🔑 Custom Mint Keypair Examples")
    print("=" * 50)
    
    choice = input("""
Choose an example:
1. Custom mint keypair
2. Auto-generated mint (default behavior)
3. Deterministic mint from seed
Enter choice (1-3): """).strip()
    
    if choice == "1":
        await example_with_custom_mint()
    elif choice == "2":
        await example_with_generated_mint()
    elif choice == "3":
        await example_deterministic_mint()
    else:
        print("Running all examples...")
        await example_with_custom_mint()
        print("\n" + "-" * 30 + "\n")
        await example_with_generated_mint()
        print("\n" + "-" * 30 + "\n")
        await example_deterministic_mint()

if __name__ == "__main__":
    asyncio.run(main())
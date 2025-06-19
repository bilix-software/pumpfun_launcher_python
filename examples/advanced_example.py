"""
Advanced example showing error handling and retry logic.
"""

import asyncio
import os
import time
from typing import Optional
from pump_fun_launcher import launch_token, TokenConfig, LaunchResult

async def launch_with_retry(
    config: TokenConfig, 
    private_key: str, 
    max_retries: int = 3,
    rpc_url: Optional[str] = None
) -> LaunchResult:
    """Launch token with retry logic."""
    
    for attempt in range(max_retries):
        print(f"🔄 Attempt {attempt + 1}/{max_retries}")
        
        result = await launch_token(config, private_key, rpc_url)
        
        if result.success:
            return result
        
        print(f"❌ Attempt {attempt + 1} failed: {result.error}")
        
        if attempt < max_retries - 1:
            wait_time = (attempt + 1) * 2  # Exponential backoff
            print(f"⏳ Waiting {wait_time} seconds before retry...")
            await asyncio.sleep(wait_time)
    
    return result  # Return the last failed result

async def main():
    """Advanced example with retry logic and error handling."""
    
    # Multiple token configurations for batch launching
    configs = [
        TokenConfig(
            name="Alpha Token",
            symbol="ALPHA",
            metadata_url="https://arweave.net/alpha-metadata",
            initial_buy=0.001,
            priority_fee=0.0005
        ),
        TokenConfig(
            name="Beta Token", 
            symbol="BETA",
            metadata_url="https://arweave.net/beta-metadata",
            initial_buy=0.002,
            priority_fee=0.0005
        ),
    ]
    
    private_key = os.getenv("SOLANA_PRIVATE_KEY")
    if not private_key:
        print("Please set SOLANA_PRIVATE_KEY environment variable")
        return
    
    results = []
    
    for i, config in enumerate(configs, 1):
        print(f"\n🚀 Launching token {i}/{len(configs)}: {config.name}")
        print("-" * 40)
        
        try:
            result = await launch_with_retry(
                config, 
                private_key, 
                max_retries=3,
                rpc_url="https://api.mainnet-beta.solana.com"
            )
            
            results.append((config, result))
            
            if result.success:
                print(f"✅ {config.name} launched successfully!")
            else:
                print(f"❌ {config.name} failed after all retries")
            
            # Wait between launches to avoid rate limiting
            if i < len(configs):
                print("⏳ Waiting 5 seconds before next launch...")
                await asyncio.sleep(5)
                
        except Exception as e:
            print(f"❌ Unexpected error launching {config.name}: {e}")
            results.append((config, LaunchResult(success=False, error=str(e))))
    
    # Summary report
    print("\n" + "=" * 60)
    print("📊 LAUNCH SUMMARY")
    print("=" * 60)
    
    successful = 0
    failed = 0
    
    for config, result in results:
        if result.success:
            successful += 1
            print(f"✅ {config.name} ({config.symbol})")
            print(f"   Token: {result.token_address}")
            print(f"   Tx: {result.signature}")
        else:
            failed += 1
            print(f"❌ {config.name} ({config.symbol})")
            print(f"   Error: {result.error}")
        print()
    
    print(f"📈 Results: {successful} successful, {failed} failed")

if __name__ == "__main__":
    asyncio.run(main())

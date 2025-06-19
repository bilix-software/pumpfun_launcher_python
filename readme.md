# Pump.Fun Token Launcher (Python)

[![PyPI version](https://badge.fury.io/py/pump-fun-token-launcher.svg?cache=bust)](https://badge.fury.io/py/pump-fun-token-launcher)
[![Python](https://img.shields.io/pypi/pyversions/pump-fun-token-launcher.svg?cache=bust)](https://pypi.org/project/pump-fun-token-launcher/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Solana](https://img.shields.io/badge/Solana-Compatible-purple.svg)](https://solana.com/)

A clean Python package for programmatically launching tokens on pump.fun.

## Features

- 🚀 Simple, intuitive API
- 🔧 Comprehensive error handling
- 📦 Clean package structure
- 🧪 Full test coverage
- 📖 Extensive documentation
- 🔄 Retry logic for reliability
- ⚡ Built on solders for performance
- 🔑 Custom mint keypair support

## Installation

```bash
pip install pump-fun-token-launcher
```

### Requirements

- Python 3.8+
- A Solana wallet with sufficient SOL balance
- Valid Solana RPC endpoint access

## Quick Start

### Basic Usage

```python
import asyncio
from pump_fun_launcher import launch_token, TokenConfig

async def main():
    config = TokenConfig(
        name="My Awesome Token",
        symbol="MAT",
        metadata_url="https://arweave.net/your-metadata-hash",
        initial_buy=0.001,  # SOL amount for initial buy
        priority_fee=0.0001  # SOL amount for priority fee
    )
    
    private_key = "your_base58_or_base64_encoded_private_key"
    
    result = await launch_token(config, private_key)
    
    if result.success:
        print(f"🎉 Success! Token: {result.token_address}")
        print(f"Transaction: {result.signature}")
        print(f"View on Pump.fun: https://pump.fun/{result.token_address}")
    else:
        print(f"❌ Failed: {result.error}")

asyncio.run(main())
```

### Using Environment Variables

```python
import os
import asyncio
from pump_fun_launcher import launch_token, TokenConfig

async def main():
    config = TokenConfig(
        name="My Token",
        symbol="MTK", 
        metadata_url="https://arweave.net/metadata-hash",
        initial_buy=0.001
    )
    
    # Use environment variable for private key
    private_key = os.getenv("SOLANA_PRIVATE_KEY")
    
    result = await launch_token(config, private_key)
    print(result)  # Pretty printed result

asyncio.run(main())
```

### Custom Mint Keypair

```python
from solders.keypair import Keypair
from pump_fun_launcher import launch_token, TokenConfig

async def main():
    # Generate or provide your own mint keypair
    custom_mint = Keypair()
    print(f"Custom mint address: {custom_mint.pubkey()}")
    
    config = TokenConfig(
        name="Custom Mint Token",
        symbol="CMT",
        metadata_url="https://arweave.net/metadata-hash",
        initial_buy=0.001,
        mint_keypair=custom_mint  # ← Use custom mint
    )
    
    result = await launch_token(config, private_key)
    if result.success:
        print(f"Token created at: {result.token_address}")
        # result.token_address == str(custom_mint.pubkey())

asyncio.run(main())
```

## Package Structure

```
pump_fun_launcher/
├── __init__.py          # Main exports
├── launcher.py          # Core launch functionality  
├── config.py           # Configuration classes
├── types.py            # Type definitions
├── constants.py        # Solana program constants
├── utils.py            # Utility functions
└── instructions.py     # Solana instruction builders

examples/
├── basic_example.py     # Simple launch example
├── interactive_example.py  # CLI interactive launcher
├── advanced_example.py  # Batch launches with retry logic
├── custom_mint_example.py  # Custom mint keypair examples
└── batch_with_custom_mints.py  # Batch launch with custom mints

tests/
├── test_config.py      # Configuration tests
├── test_utils.py       # Utility function tests
├── test_custom_mint.py # Custom mint tests
└── conftest.py         # Test configuration
```

## API Reference

### `TokenConfig`

```python
@dataclass
class TokenConfig:
    name: str                        # Token name (required)
    symbol: str                      # Token symbol (required, max 10 chars)
    metadata_url: str                # Token metadata URL (required)
    initial_buy: float = 0.01        # Initial buy amount in SOL
    priority_fee: float = 0.001      # Priority fee in SOL
    mint_keypair: Optional[Keypair] = None  # Custom mint keypair (optional)
```

### `launch_token()`

```python
async def launch_token(
    config: TokenConfig,
    private_key: Union[str, Keypair],
    rpc_url: str = "https://api.mainnet-beta.solana.com"
) -> LaunchResult
```

### `LaunchResult`

```python
@dataclass 
class LaunchResult:
    success: bool
    signature: Optional[str] = None
    token_address: Optional[str] = None  
    error: Optional[str] = None
```

## Examples

### Run Interactive Example

```bash
python examples/interactive_example.py
```

This will guide you through token creation with prompts for all parameters.

### Custom Mint Examples

```bash
python examples/custom_mint_example.py
```

Choose from:
- Custom mint keypair generation
- Auto-generated mint (default)
- Deterministic mint from seed

### Batch Token Launch

```python
# See examples/advanced_example.py for full implementation
configs = [
    TokenConfig(name="Alpha Token", symbol="ALPHA", metadata_url="..."),
    TokenConfig(name="Beta Token", symbol="BETA", metadata_url="..."),
]

for config in configs:
    result = await launch_with_retry(config, private_key, max_retries=3)
    print(f"Token {config.name}: {'✅' if result.success else '❌'}")
```

### Batch with Custom Mints

```python
# Assign specific mint addresses to each token
tokens = [
    (TokenConfig(name="Alpha", symbol="A", ...), Keypair()),
    (TokenConfig(name="Beta", symbol="B", ...), Keypair()),
]

for config, mint in tokens:
    config.mint_keypair = mint
    result = await launch_token(config, private_key)
    print(f"Token {config.name} at {result.token_address}")
```

## Mint Keypair Options

### Auto-Generated (Default)
```python
config = TokenConfig(name="Token", symbol="TKN", metadata_url="...")
# mint_keypair is None, so a random one will be generated
```

### Custom Keypair
```python
from solders.keypair import Keypair

custom_mint = Keypair()
config = TokenConfig(
    name="Token", 
    symbol="TKN", 
    metadata_url="...",
    mint_keypair=custom_mint
)
```

### Deterministic from Seed
```python
seed = "my-reproducible-seed".encode('utf-8')[:32].ljust(32, b'\0')
deterministic_mint = Keypair.from_bytes(seed)
config = TokenConfig(
    name="Token",
    symbol="TKN", 
    metadata_url="...",
    mint_keypair=deterministic_mint
)
# Always creates the same token address!
```

## Development

### Setup Development Environment

```bash
git clone https://github.com/bilix-software/pump-fun-token-launcher-python.git
cd pump-fun-token-launcher-python
pip install -e .[dev]
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black pump_fun_launcher/
isort pump_fun_launcher/
```

### Type Checking

```bash
mypy pump_fun_launcher/
```

## Error Handling

The package includes comprehensive error handling:

```python
result = await launch_token(config, private_key)

if not result.success:
    if "insufficient" in result.error.lower():
        print("💰 Insufficient wallet balance")
    elif "invalid" in result.error.lower():
        print("🔑 Invalid configuration or private key")
    elif "timeout" in result.error.lower():
        print("⏰ Transaction timed out - try increasing priority fee")
    else:
        print(f"❌ Launch failed: {result.error}")
```

## Environment Setup

1. **Get SOL**: Ensure your wallet has sufficient SOL for:
   - Transaction fees (~0.01 SOL)
   - Initial token purchase (if specified)
   - Priority fees

2. **Private Key**: Set your private key as an environment variable:
   ```bash
   export SOLANA_PRIVATE_KEY="your_base58_or_base64_key_here"
   ```

3. **Metadata**: Upload your token metadata to IPFS or Arweave and use that URL.

## Dependencies

- `solana` - Core Solana Python library
- `solders` - Fast Solana primitives  
- `base58` - Base58 encoding/decoding

## License

MIT License - see LICENSE file for details.

## Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/bilix-software/pump-fun-token-launcher-python/issues)
- 💬 **Telegram**: [@bilixsoftware](https://t.me/bilixsoftware)  
- 📧 **Email**: info@bilix.io

## Contributing

Contributions welcome! Please read the contributing guidelines and submit pull requests.

---

**⚠️ Disclaimer**: This tool is for educational purposes. Always test on devnet first. Cryptocurrency development involves financial risk.

## Tips

JATt1ta9GcbVMThdL18rXUqHn3toCMjWkHWtxM5WN3ec

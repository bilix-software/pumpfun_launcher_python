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

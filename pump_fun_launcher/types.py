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

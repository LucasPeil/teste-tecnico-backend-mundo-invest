from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class UseCaseResponse:
    message: str
    status_code: int
    response: Optional[Any] = None

from dataclasses import dataclass
from typing import Optional

@dataclass
class SpeechToLatexResponse:
    success: bool
    transcript: str
    latex: str
    error: Optional[str] = None

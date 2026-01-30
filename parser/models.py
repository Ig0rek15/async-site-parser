from dataclasses import dataclass
from typing import List


@dataclass(slots=True)
class ParseResult:
    url: str
    emails: List[str]
    phones: List[str]

from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class AnalysisRequest(BaseModel):
    url: Optional[HttpUrl] = None
    text: Optional[str] = None

class Highlight(BaseModel):
    sentence: str
    reason: str
    claim: Optional[str] = None

class AnalysisResult(BaseModel):
    label: str
    confidence: float
    summary: str
    explanation: List[str]
    highlights: List[Highlight]
    raw: dict
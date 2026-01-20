from pydantic import BaseModel
from typing import List, Literal, Optional

class DebugInput(BaseModel):
    language: str
    error_logs: str

class ErrorClassification(BaseModel):
    category: Literal[
        "syntax_error",
        "runtime_error",
        "dependency_error",
        "configuration_error",
        "unknown"
    ]
    confidence: float

class RootCause(BaseModel):
    summary: str
    detailed_explanation: str

class FixSuggestion(BaseModel):
    steps: List[str]
    code_example: Optional[str] = None

class PreventionTips(BaseModel):
    tips: List[str]

class DebugResponse(BaseModel):
    classification: ErrorClassification
    root_cause: RootCause
    fix: FixSuggestion
    prevention: PreventionTips

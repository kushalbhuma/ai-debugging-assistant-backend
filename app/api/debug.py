from fastapi import APIRouter
from app.schemas.debug import DebugInput, DebugResponse, ErrorClassification, RootCause, FixSuggestion, PreventionTips
from app.agents.classifier import classify_error
from app.agents.root_cause import analyze_root_cause
from app.agents.fixer import suggest_fix
from app.agents.prevention import suggest_prevention
import json

router = APIRouter()

@router.post("/debug")
async def debug_error(request: DebugInput) -> DebugResponse:
    try:
        classification_str = await classify_error(request.error_logs, request.language)
        root_cause_str = await analyze_root_cause(request.error_logs, request.language)
        fix_str = await suggest_fix(request.error_logs, request.language)
        prevention_str = await suggest_prevention(request.error_logs, request.language)
        
        classification_data = json.loads(classification_str)
        root_cause_data = json.loads(root_cause_str)
        fix_data = json.loads(fix_str)
        prevention_data = json.loads(prevention_str)
        
        return DebugResponse(
            classification=ErrorClassification(**classification_data),
            root_cause=RootCause(**root_cause_data),
            fix=FixSuggestion(**fix_data),
            prevention=PreventionTips(**prevention_data)
        )
    except Exception as e:
        print(f"DEBUG: Exception occurred: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return DebugResponse(
            classification=ErrorClassification(category="unknown", confidence=0.0),
            root_cause=RootCause(summary="Error", detailed_explanation=str(e)),
            fix=FixSuggestion(steps=["Try again"]),
            prevention=PreventionTips(tips=["Check logs"])
        )

@router.get("/health")
async def health():
    return {"status": "ok"}

import redis.asyncio as redis
import hashlib
from datetime import datetime
from fastapi import BackgroundTasks
# from fastapi_cache.decorator import cache                   #caching import
from fastapi import APIRouter
from app.schemas.debug import DebugInput, DebugResponse, ErrorClassification, RootCause, FixSuggestion, PreventionTips
from app.agents.classifier import classify_error
from app.agents.root_cause import analyze_root_cause
from app.agents.fixer import suggest_fix
from app.agents.prevention import suggest_prevention
import json
from app.utils.logger import logger
from fastapi import HTTPException
from jose import jwt, JWTError
from app.utils.auth import SECRET_KEY, ALGORITHM
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

router = APIRouter()

def save_debug_log(language: str, error_logs: str): 
    logger.info(f"{datetime.now()} Background saved debug request for {language} | {error_logs[:100]}")

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)

@router.post("/debug")

async def debug_error(
    payload: DebugInput,
    background_tasks: BackgroundTasks,
    user = Depends(verify_token)
) -> DebugResponse:

    try:
        logger.info(f"{datetime.now()} REQUEST RECEIVED")

        error_logs = payload.error_logs
        language = payload.language

        # Build cache key from request
        raw_key = f"{language}:{error_logs}"
        cache_key = "debug:" + hashlib.sha256(raw_key.encode()).hexdigest()

        # Check Redis first
        cached_result = await redis_client.get(cache_key)

        if cached_result:
            logger.info("CACHE HIT - Returning from Redis")
            return DebugResponse(**json.loads(cached_result))
        
        background_tasks.add_task(save_debug_log,language,error_logs)

        classification_str = await classify_error(error_logs, language)
        root_cause_str = await analyze_root_cause(error_logs, language)
        fix_str = await suggest_fix(error_logs, language)
        prevention_str = await suggest_prevention(error_logs, language)
        
        logger.info(f"{datetime.now()} AI PROCESSING COMPLETED")

        classification_data = json.loads(classification_str)
        root_cause_data = json.loads(root_cause_str)
        fix_data = json.loads(fix_str)
        prevention_data = json.loads(prevention_str)
        
        result_data = {
                "classification": classification_data,
                "root_cause": root_cause_data,
                "fix": fix_data,
                "prevention": prevention_data
            }

        # Store in Redis for 5 minutes
        await redis_client.set(
         cache_key,
        json.dumps(result_data),
        ex=300
        )

        return DebugResponse(**result_data)

    except Exception as e:
       
        logger.exception("Error occurred while processing request")

        error_msg = str(e).lower()

        if "rate limit" in error_msg:
            raise HTTPException(
                status_code=429, 
                detail="AI rate limit exceeded"
                )

        if "model" in error_msg or "provider" in error_msg:
            raise HTTPException(
                status_code=502, 
                detail="AI service unavailable"
                )
        
        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing debug request"
            )

@router.get("/health")
async def health():
    return {"status": "ok"}

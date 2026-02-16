from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.debug import router
from app.api.health import health_router
from fastapi_cache import FastAPICache
# from fastapi_cache.backends.inmemory import InMemoryBackend   -- earlier I tried to save the cache in memory itself but it was not working, so I switched to Redis
from fastapi_cache.backends.redis import RedisBackend  # this too was not working when I tried caching like its taking time when I paste the same input again 2nd time its loading slow.
import redis.asyncio as redis
from fastapi.openapi.utils import get_openapi
from app.api.auth import router as auth_router



app = FastAPI(title="AI Debugging Assistant", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(health_router)
app.include_router(auth_router)

# @app.on_event("startup")
# async def startup():
#                                                              -- earlier I tried to save the cache in memory itself but it was not working, so I switched to Redis
  # This creates a cache stored in server RAM                
#     FastAPICache.init(InMemoryBackend())

@app.on_event("startup")
async def startup():
    redis_client = redis.from_url("redis://localhost:6379")     
    FastAPICache.init(RedisBackend(redis_client))



def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="AI Debugging Assistant",
        version="0.1.0",
        description="AI Debugging Backend with JWT Authentication",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


from fastapi import APIRouter, Depends
from rate_limiter_service.service import RateLimiterDependency

router = APIRouter(prefix="/demo-service")

@router.get("/hello", dependencies=[Depends(RateLimiterDependency(calls_per_minute=5))])
async def hello():
    return {"message": "Hello from Demo Service!"}
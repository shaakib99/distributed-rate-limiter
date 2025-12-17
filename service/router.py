from fastapi import APIRouter, Depends, Request
from rate_limiter_service.service import RateLimiterDependency
import asyncio

router = APIRouter(prefix="/demo-service")

@router.get("/hello", dependencies=[Depends(RateLimiterDependency(calls_per_minute=5))])
async def hello(request: Request):
    await asyncio.sleep(2) 
    return {"message": "Hello from Demo Service!"}
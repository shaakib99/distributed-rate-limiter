from datetime import datetime, timezone, timedelta
from rate_limiter_service.redis_service import RedisService
import json
from fastapi import Request, HTTPException

class RateLimiter:
    def __init__(self, calls_per_minute: int):
        self.redis_service = RedisService()
        self.calls_per_minute = calls_per_minute
        self.window_seconds = 60

    async def is_rate_limited(self, client_id: str) -> bool:
        key = f"rate_limit:{client_id}"

        # Atomic increment — this is safe under concurrency
        new_count = await self.redis_service.incr(key)

        # Set TTL only on the very first request (when count goes from 0 → 1)
        if new_count == 1:
            await self.redis_service.expire(key, self.window_seconds)

        # If we've exceeded the limit, block
        if new_count > self.calls_per_minute:
            return True

        return False


class RateLimiterDependency:
    def __init__(self, calls_per_minute: int):
        self.rate_limiter_service = RateLimiter(calls_per_minute)
        self.calls_per_minute = calls_per_minute

    async def __call__(self, request: Request):
        if request.client is None:
            raise HTTPException(status_code=400, detail="Unable to determine client IP")
        
        client_id = request.client.host

        if await self.rate_limiter_service.is_rate_limited(client_id):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

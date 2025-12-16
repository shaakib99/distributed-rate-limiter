from datetime import datetime, timezone, timedelta
from rate_limiter_service.redis_service import RedisService
import json
from fastapi import Request, HTTPException

class RateLimiter:
    def __init__(self, calls_per_minute: int):
        self.redis_service = RedisService()
        self.calls_per_minute = calls_per_minute

    async def is_rate_limited(self, id: str) -> bool:
        key = f"rate_limit:{id}"
        time_format = "%Y-%m-%dT%H:%M:%S.%f%z"
        current_time = datetime.now(timezone.utc)
        window_start = current_time - timedelta(minutes=1)
        if not await self.redis_service.has(key):
            await self.redis_service.set(key, json.dumps({"count": 1, "last_modified": current_time.strftime(time_format)}), ex=60)
            return False
        else:
            data = await self.redis_service.get(key)
            if data is None:
                await self.redis_service.set(key, json.dumps({"count": 1, "last_modified": current_time.strftime(time_format)}), ex=60)
                return False

            data = json.loads(data)
            count = data["count"]
            print(count)
            last_modified = datetime.fromisoformat(data["last_modified"])
            if count < self.calls_per_minute and last_modified > window_start:
                await self.redis_service.set(key, json.dumps({"count": count + 1, "last_modified": current_time.strftime(time_format)}), ex=60)
                return False
            
            return True 

from fastapi import Request, HTTPException

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

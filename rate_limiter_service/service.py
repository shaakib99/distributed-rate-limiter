from datetime import datetime, timezone, timedelta
from redis_service import RedisService
import json

class RateLimiter:
    def __init__(self, calls_per_minute: int):
        self.redis_service = RedisService()
        self.calls_per_minute = calls_per_minute

    async def is_rate_limited(self, id: str) -> bool:
        key = f"rate_limit:{id}"
        current_time = datetime.now(timezone.utc)
        window_start = current_time - timedelta(minutes=1)
        if not await self.redis_service.has(key):
            await self.redis_service.set(key, json.dumps({"count": 1, "last_modified": current_time}), ex=60)
            return False
        else:
            data = await self.redis_service.get(key)
            if data is None:
                await self.redis_service.set(key, json.dumps({"count": 1, "last_modified": current_time}), ex=60)
                return False

            data = json.loads(data)
            count = data["count"]
            last_modified = datetime.fromisoformat(data["last_modified"])
            if count < self.calls_per_minute and last_modified > window_start:
                await self.redis_service.set(key, json.dumps({"count": count + 1, "last_modified": current_time}), ex=60)
                return False
            
            return True 
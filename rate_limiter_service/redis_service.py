from redis.asyncio import RedisCluster
from redis.asyncio.cluster import ClusterNode

class RedisService:
    def __init__(self):
        self.client: RedisCluster = RedisCluster(
           startup_nodes=[
                ClusterNode(host="localhost", port=7000),
                ClusterNode(host="localhost", port=7001),
                ClusterNode(host="localhost", port=7002),
            ],
            decode_responses=True,
        )

    async def connect(self):
        return await self.client.ping()
    
    async def disconnect(self):
        return await self.client.close()
    
    async def get(self, key: str) -> str | None:
        result = await self.client.get(key)
        if result is None:
            return None
        if isinstance(result, bytes):
            return result.decode()
        return str(result)
    
    async def set(self, key: str, value: str, ex: int = 0):
        if ex:
            await self.client.set(key, value, ex=ex)
        else:
            await self.client.set(key, value)
    
    async def has(self, key: str) -> bool:
        return (await self.client.exists(key)) == 1
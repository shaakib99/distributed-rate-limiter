from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from service.router import router as demo_router
from rate_limiter_service.redis_service import RedisService

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    redis_service = RedisService()
    await redis_service.connect()
    yield

app = FastAPI(lifespan=lifespan)

routers = [demo_router]
for r in routers:
    app.include_router(r)


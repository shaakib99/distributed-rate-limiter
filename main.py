from fastapi import FastAPI
from dotenv import load_dotenv
from .service.router import router as demo_router

load_dotenv()
app = FastAPI()

routers = [demo_router]
for r in routers:
    app.include_router(r)


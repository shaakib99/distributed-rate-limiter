from fastapi import APIRouter

router = APIRouter(prefix="/demo-service")

@router.get("/hello")
async def hello():
    return {"message": "Hello from Demo Service!"}
from  fastapi import APIRouter

router = APIRouter()

@router.get("/")
def docs():
    return {"docs": []}
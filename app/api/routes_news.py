from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
def news_route_status():
    return {"message": "News classification routes are working!"}
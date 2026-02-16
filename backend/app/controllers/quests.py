from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def list_quests():
    return {"message": "quests endpoint (placeholder)"}

from fastapi import APIRouter
from .. import db
from sqlalchemy import text

router = APIRouter()


@router.get("/check")
def check_db():
    """Attempt a quick DB connection and return status."""
    try:
        with db.engine.connect() as conn:
            r = conn.execute(text("SELECT 1")).scalar()
        return {"db_ok": True, "test_query": int(r)}
    except Exception as e:
        return {"db_ok": False, "error": str(e)}


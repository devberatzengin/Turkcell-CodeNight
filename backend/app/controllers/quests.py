from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from .. import db
from sqlalchemy import text

router = APIRouter()


@router.get("/")
def list_quests(active_only: bool = Query(False)):
    """List all quests, optionally filtered to active only."""
    with db.engine.connect() as conn:
        if active_only:
            rows = conn.execute(text(
                'SELECT quest_id, quest_name, quest_type, condition, reward_points, priority, is_active '
                'FROM quests WHERE is_active = true ORDER BY priority ASC'
            )).fetchall()
        else:
            rows = conn.execute(text(
                'SELECT quest_id, quest_name, quest_type, condition, reward_points, priority, is_active '
                'FROM quests ORDER BY priority ASC'
            )).fetchall()
    return [dict(r._mapping) for r in rows]


@router.get("/{quest_id}")
def get_quest(quest_id: str):
    """Get a single quest by ID."""
    with db.engine.connect() as conn:
        row = conn.execute(text(
            'SELECT quest_id, quest_name, quest_type, condition, reward_points, priority, is_active '
            'FROM quests WHERE quest_id = :q'
        ), {'q': quest_id}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail='quest not found')
    return dict(row._mapping)


class QuestUpdate(BaseModel):
    quest_name: Optional[str] = None
    quest_type: Optional[str] = None
    condition: Optional[str] = None
    reward_points: Optional[int] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None


@router.put("/{quest_id}")
def update_quest(quest_id: str, body: QuestUpdate):
    """Update quest fields (name, type, condition, reward, priority, active)."""
    with db.engine.begin() as conn:
        existing = conn.execute(text('SELECT 1 FROM quests WHERE quest_id = :q'), {'q': quest_id}).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail='quest not found')

        updates = {}
        if body.quest_name is not None:
            updates['quest_name'] = body.quest_name
        if body.quest_type is not None:
            updates['quest_type'] = body.quest_type
        if body.condition is not None:
            updates['condition'] = body.condition
        if body.reward_points is not None:
            updates['reward_points'] = body.reward_points
        if body.priority is not None:
            updates['priority'] = body.priority
        if body.is_active is not None:
            updates['is_active'] = body.is_active

        if not updates:
            return {"message": "no fields to update"}

        set_clause = ', '.join([f"{k} = :{k}" for k in updates])
        updates['quest_id'] = quest_id
        conn.execute(text(f"UPDATE quests SET {set_clause} WHERE quest_id = :quest_id"), updates)

    return {"message": f"quest {quest_id} updated", "updated_fields": list(updates.keys())}


@router.patch("/{quest_id}/toggle")
def toggle_quest(quest_id: str):
    """Toggle a quest's active status."""
    with db.engine.begin() as conn:
        row = conn.execute(text('SELECT is_active FROM quests WHERE quest_id = :q'), {'q': quest_id}).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail='quest not found')

        current_active = dict(row._mapping).get('is_active', False)
        new_status = not current_active
        conn.execute(text('UPDATE quests SET is_active = :s WHERE quest_id = :q'), {'s': new_status, 'q': quest_id})

    return {"quest_id": quest_id, "is_active": new_status}

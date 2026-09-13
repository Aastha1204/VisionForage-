from fastapi import APIRouter, HTTPException

from app.core.tasks import TASKS, TASKS_BY_ID

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("")
def list_tasks():
    return {"tasks": TASKS}


@router.get("/{task_id}")
def get_task(task_id: str):
    task = TASKS_BY_ID.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Unknown task '{task_id}'")
    return task

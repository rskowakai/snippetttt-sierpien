from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
from ..celery_app import celery_app
from .. import schemas

router = APIRouter()

@router.get("/{task_id}", response_model=schemas.TaskRead, tags=["Tasks"])
async def get_task_status(task_id: str):
    """
    Get the status of a Celery task by its ID.
    """
    task_result = AsyncResult(task_id, app=celery_app)

    if not task_result:
        raise HTTPException(status_code=404, detail="Task not found")

    response = {
        "task_id": task_id,
        "status": task_result.status,
        "task_type": task_result.name or "unknown", # task_result.name might be None
        "created_at": "N/A", # Celery doesn't easily expose creation time
        "error_message": str(task_result.info) if task_result.failed() else None,
    }

    return response

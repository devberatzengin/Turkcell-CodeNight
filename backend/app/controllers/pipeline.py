from fastapi import APIRouter, BackgroundTasks, Query
from ..services import pipeline as pipeline_svc
from ..schemas import PipelineRunResponse

router = APIRouter()


@router.post("/run", response_model=PipelineRunResponse)
def run_pipeline(background_tasks: BackgroundTasks, as_of_date: str = None, sync: bool = Query(False)):
    """Trigger the ingestion + pipeline run.

    If `sync=true` the pipeline runs synchronously and returns a summary.
    Otherwise it is scheduled as a background task and returns started status.
    """
    if sync:
        res = pipeline_svc.run_pipeline(as_of_date)
        return {"status": "completed", "processed_users": int(res.get('processed_users', 0)), "message": "pipeline completed"}

    background_tasks.add_task(pipeline_svc.run_pipeline, as_of_date)
    return {"status": "started", "processed_users": 0, "message": "pipeline started in background"}

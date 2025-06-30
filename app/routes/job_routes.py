from fastapi import APIRouter, WebSocket, HTTPException, Body
from app.services.scheduler_service import (
    submit_job, get_job, list_jobs, cancel_job, get_logs, job_streamer
)

router = APIRouter()

@router.post("/")
async def create_jobs(jobs_data: list[dict] = Body(...)):
    results = []
    for job_data in jobs_data:
        result = await submit_job(job_data)
        results.append(result)
    return results

@router.get("/{job_id}")
async def get_job_status(job_id: str):
    job = await get_job(job_id)
    return job

@router.get("/list")
async def list_all_jobs():
    jobs = await list_jobs()
    return jobs

@router.patch("/{job_id}/cancel")
async def cancel(job_id: str):
    return await cancel_job(job_id)

@router.get("/{job_id}/logs")
async def logs(job_id: str):
    return await get_logs(job_id)

@router.websocket("/stream")
async def stream_jobs(ws: WebSocket):
    await job_streamer(ws)
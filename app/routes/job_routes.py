from fastapi import APIRouter, WebSocket, HTTPException
from app.services.scheduler_service import (
    submit_job, get_job, list_jobs, cancel_job, get_logs, job_streamer
)

router = APIRouter()

@router.post("/")
async def create_job(job_data: dict):
    return await submit_job(job_data)

@router.get("/{job_id}")
async def get_job_status(job_id: str):
    return await get_job(job_id)

@router.get("/list")
async def list_all_jobs():
    return await list_jobs()

@router.patch("/{job_id}/cancel")
async def cancel(job_id: str):
    return await cancel_job(job_id)

@router.get("/{job_id}/logs")
async def logs(job_id: str):
    return await get_logs(job_id)

@router.websocket("/stream")
async def stream_jobs(ws: WebSocket):
    await job_streamer(ws)
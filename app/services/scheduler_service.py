from fastapi import HTTPException
import uuid, asyncio
from sqlalchemy import select
from app.models.job import ScheduledJobs, JobMonitoring, JobTracker
from app.db_connection import SessionLocal

SYSTEM_RESOURCES = {"cpu_units": 8, "memory_mb": 4096}
current_usage = {"cpu_units": 0, "memory_mb": 0}

PRIORITY_ORDER = {"critical": 0, "high": 1, "normal": 2, "low": 3}

def priority_sort_key(job):
    return PRIORITY_ORDER.get(job.priority, 99)

async def submit_job(job_data):
    db = SessionLocal()
    job_id = job_data.get("job_id") or f"job_{uuid.uuid4().hex[:8]}"
    depends_on = job_data.get("depends_on", [])
    status = JobTracker.BLOCKED if depends_on else JobTracker.READY

    # Extract resource fields
    resource_fields = ['resource_cpu', 'resource_memory']  # Add more as needed
    resource_requirements = {k: job_data.pop(k) for k in resource_fields if k in job_data}

    # Prepare job_data for model
    job_fields = {c.name for c in ScheduledJobs.__table__.columns}
    filtered_job_data = {k: v for k, v in job_data.items() if k in job_fields}
    filtered_job_data['resource_requirements'] = resource_requirements

    job = ScheduledJobs(id=job_id, status=status, **filtered_job_data)
    db.add(job)
    db.commit()
    return {
        "job_id": job_id,
        "status": job.status.value,
        "created_at": getattr(job, "created_at", None),
        "priority": job.priority
    }

async def get_job(job_id):
    db = SessionLocal()
    return db.query(ScheduledJobs).filter(ScheduledJobs.id == job_id).first()

def list_jobs():
    db = SessionLocal()
    try:
        jobs = db.query(ScheduledJobs).all()
        return jobs
    finally:
        db.close()

async def cancel_job(job_id):
    db = SessionLocal()
    job = db.query(ScheduledJobs).filter(ScheduledJobs.id == job_id).first()
    if job.status in [JobTracker.PENDING, JobTracker.RUNNING, JobTracker.READY]:
        job.status = JobTracker.CANCELED
        db.commit()
        return {"status": "canceled"}
    raise HTTPException(status_code=400, detail="Cannot cancel job")

async def get_logs(job_id):
    db = SessionLocal()
    logs = db.query(JobMonitoring).filter(JobMonitoring.job_id == job_id).all()
    return [l.message for l in logs]

async def job_streamer(ws):
    await ws.accept()
    while True:
        await ws.send_json({"msg": "Job updates coming soon"})
        await asyncio.sleep(5)

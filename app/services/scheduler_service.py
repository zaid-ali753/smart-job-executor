import uuid, asyncio
from sqlalchemy import select
from app.models.job import ScheduledJobs, JobMonitoring, JobTracker
from app.db_connection import SessionLocal

async def submit_job(job_data):
    db = SessionLocal()
    job_id = f"job_{uuid.uuid4().hex[:8]}"
    job = ScheduledJobs(id=job_id, **job_data)
    db.add(job)
    db.commit()
    return {
        "job_id": job_id,
        "status": job.status,
        "created_at": job.created_at,
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
    if job.status in [JobTracker.PENDING, JobTracker.RUNNING]:
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

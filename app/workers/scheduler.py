import asyncio
from app.db_connection import SessionLocal
from app.models.job import ScheduledJobs, JobTracker, JobMonitoring
import logging
logging.basicConfig(level=logging.INFO)

resources = {"cpu": 8, "memory": 16000}
used = {"cpu": 0, "memory": 0}

async def execute_job(job):
    db = SessionLocal()
    job.status = JobTracker.RUNNING
    db.commit()
    await asyncio.sleep(2)  
    job.status = JobTracker.COMPLETED
    log = JobMonitoring(job_id=job.id, message="Completed successfully")
    db.add(log)
    db.commit()

async def start_scheduler():
    async def scheduler_loop():
        while True:
            db = SessionLocal()
            jobs = db.query(ScheduledJobs).filter(ScheduledJobs.status == JobTracker.PENDING).all()
            for job in sorted(jobs, key=lambda j: j.priority):
                if job.resource_cpu + used["cpu"] <= resources["cpu"] and \
                   job.resource_memory + used["memory"] <= resources["memory"]:
                    used["cpu"] += job.resource_cpu
                    used["memory"] += job.resource_memory
                    asyncio.create_task(execute_job(job))
            await asyncio.sleep(5)
    asyncio.create_task(scheduler_loop())
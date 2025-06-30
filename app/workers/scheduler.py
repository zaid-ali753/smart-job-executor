import asyncio
from app.db_connection import SessionLocal
from app.models.job import ScheduledJobs, JobTracker
from app.models.job import JobMonitoring
import datetime

SYSTEM_RESOURCES = {"cpu_units": 8, "memory_mb": 4096}
current_usage = {"cpu_units": 0, "memory_mb": 0}
PRIORITY_ORDER = {"critical": 0, "high": 1, "normal": 2, "low": 3}

def log_job_event(db, job_id, message):
    log = JobMonitoring(
        job_id=job_id,
        timestamp=datetime.datetime.utcnow(),
        message=message
    )
    db.add(log)
    db.commit()

def priority_sort_key(job):
    return PRIORITY_ORDER.get(job.priority, 99)

def resolve_dependencies(db):
    blocked_jobs = db.query(ScheduledJobs).filter(ScheduledJobs.status == JobTracker.BLOCKED).all()
    for job in blocked_jobs:
        if all_dependencies_completed(db, job.depends_on):
            job.status = JobTracker.READY
    db.commit()

def all_dependencies_completed(db, depends_on):
    if not depends_on:
        return True
    for dep_id in depends_on:
        dep = db.query(ScheduledJobs).filter(ScheduledJobs.id == dep_id).first()
        if not dep or dep.status != JobTracker.COMPLETED:
            return False
    return True

def can_allocate(job):
    req = job.resource_requirements or {}
    return (
        current_usage["cpu_units"] + req.get("cpu_units", 0) <= SYSTEM_RESOURCES["cpu_units"] and
        current_usage["memory_mb"] + req.get("memory_mb", 0) <= SYSTEM_RESOURCES["memory_mb"]
    )

def allocate_resources(job):
    req = job.resource_requirements or {}
    current_usage["cpu_units"] += req.get("cpu_units", 0)
    current_usage["memory_mb"] += req.get("memory_mb", 0)

def release_resources(job):
    req = job.resource_requirements or {}
    current_usage["cpu_units"] -= req.get("cpu_units", 0)
    current_usage["memory_mb"] -= req.get("memory_mb", 0)

async def scheduler_loop():
    while True:
        db = SessionLocal()
        try:
            resolve_dependencies(db)
            ready_jobs = db.query(ScheduledJobs).filter(ScheduledJobs.status == JobTracker.READY).all()
            ready_jobs.sort(key=priority_sort_key)
            for job in ready_jobs:
                if can_allocate(job):
                    job.status = JobTracker.RUNNING
                    allocate_resources(job)
                    db.commit()
                    asyncio.create_task(execute_job(job.id))
        finally:
            db.close()
        await asyncio.sleep(1)

async def execute_job(job_id):
    db = SessionLocal()
    job = db.query(ScheduledJobs).filter(ScheduledJobs.id == job_id).first()
    retry_cfg = job.retry_config or {}
    max_attempts = retry_cfg.get("max_attempts", 1)
    backoff = retry_cfg.get("backoff_multiplier", 1)
    delay = retry_cfg.get("initial_delay_seconds", 0)
    attempt = 0
    success = False
    log_job_event(db, job_id, "Job execution started")
    while attempt < max_attempts and not success:
        attempt += 1
        try:
            await run_job(job, job.timeout_seconds)
            job.status = JobTracker.COMPLETED
            log_job_event(db, job_id, f"Job completed successfully on attempt {attempt}")
            success = True
        except Exception as e:
            log_job_event(db, job_id, f"Job failed on attempt {attempt}: {str(e)}")
            if attempt >= max_attempts:
                job.status = JobTracker.FAILED
            else:
                await asyncio.sleep(delay)
                delay *= backoff
    release_resources(job)
    db.commit()
    db.close()

async def run_job(job, timeout):
    try:
        await asyncio.wait_for(asyncio.sleep(1), timeout=timeout)
    except asyncio.TimeoutError:
        raise Exception("Timeout")
from fastapi import FastAPI
from app.routes import job_routes
import asyncio
from app.workers.scheduler import scheduler_loop

app = FastAPI()

app.include_router(job_routes.router, prefix="/jobs")


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(scheduler_loop())

@app.get("/")
def health():
    return {"status": "ok"}
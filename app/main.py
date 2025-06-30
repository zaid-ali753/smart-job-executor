from fastapi import FastAPI
from app.routes import job_routes

app = FastAPI()

app.include_router(job_routes.router, prefix="/jobs", tags=["Jobs"])

# Run background scheduler
from app.workers.scheduler import start_scheduler

@app.on_event("startup")
async def startup_event():
    await start_scheduler()

@app.get("/")
def health():
    return {"status": "ok"}
from sqlalchemy import Column, String, Integer, DateTime, JSON, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum
import datetime

Base = declarative_base()

class JobTracker(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"

class ScheduledJobs(Base):
    __tablename__ = "scheduledJobs"

    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)
    priority = Column(String, default="normal")
    payload = Column(JSON)
    resource_cpu = Column(Integer)
    resource_memory = Column(Integer)
    depends_on = Column(JSON, default=[])
    retry_attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    backoff_multiplier = Column(Integer, default=2)
    timeout_seconds = Column(Integer, default=300)
    status = Column(Enum(JobTracker), default=JobTracker.PENDING)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    logs = relationship("JobMonitoring", back_populates="job")

class JobMonitoring(Base):
    __tablename__ = "jobMonitoring"

    id = Column(Integer, primary_key=True)
    job_id = Column(String, ForeignKey("scheduledJobs.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    message = Column(String)
    job = relationship("ScheduledJobs", back_populates="logs")
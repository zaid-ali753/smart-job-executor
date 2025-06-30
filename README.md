# smart-job-executor

A flexible, scalable job scheduling and execution system built with Python. This project allows you to define, schedule, and manage background jobs with ease, making it ideal for automation, batch processing, and workflow orchestration.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [API Usage](#api-usage)
  - [Create a Job](#create-a-job)
  - [List Jobs](#list-jobs)
  - [Get Job Status](#get-job-status)
  - [Delete a Job](#delete-a-job)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**smart-job-executor** is designed to help you manage and execute background jobs efficiently. Whether you need to run scheduled tasks, process data, or automate workflows, this system provides a robust foundation.

---

## Features

- **Job Scheduling:** Schedule jobs to run at specific times or intervals.
- **Job Management:** Create, list, update, and delete jobs via a RESTful API.
- **Extensible Workers:** Easily add new types of jobs or workers.
- **Database Integration:** Persist job data using SQLAlchemy and Alembic migrations.
- **Docker Support:** Run the entire stack with Docker Compose.

---

## Architecture

- **FastAPI** for the REST API.
- **SQLAlchemy** for ORM and database management.
- **Alembic** for database migrations.
- **Custom Scheduler** for job execution.
- **Docker** for containerized deployment.

For more details, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Getting Started

### Prerequisites

- Python 3.8+
- Docker & Docker Compose (optional, for containerized setup)

### Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/zaid-ali753/smart-job-executor.git
   cd smart-job-executor
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

4. **Start the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

### Docker Setup

1. **Build and start the services:**
   ```bash
   docker-compose up --build
   ```

---

## API Usage

Below are some example `curl` commands to interact with the API.

### Create a Job

```bash
curl -X POST "http://localhost:8000/jobs" \
     -H "Content-Type: application/json" \
     -d '{
           "name": "example-job",
           "schedule": "0 * * * *",  # every hour
           "command": "echo Hello, World!"
         }'
```

### List Jobs

```bash
curl -X GET "http://localhost:8000/jobs"
```

### Get Job Status

```bash
curl -X GET "http://localhost:8000/jobs/{job_id}"
```
Replace `{job_id}` with the actual job ID.

### Delete a Job

```bash
curl -X DELETE "http://localhost:8000/jobs/{job_id}"
```
Replace `{job_id}` with the actual job ID.

---

## Development

- Source code is in the `app/` directory.
- Database models are in `app/models/`.
- API routes are in `app/routes/`.
- Scheduler logic is in `app/services/` and `app/workers/`.

To run tests (if available):
```bash
pytest tests/
```

---

## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements or bug fixes.

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes.
4. Push to your branch and open a Pull Request.


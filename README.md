Task Routing System

A full-stack task assignment and routing platform built with FastAPI, SQLAlchemy, SQLite, and Next.js. The system automatically assigns tasks to eligible contributors based on skills, availability, and workload capacity.

Key Features

- Task creation and management
- Contributor registration and management
- Skill-based contributor matching
- Workload-aware assignment scoring
- Contributor availability and capacity enforcement
- Assignment acceptance and rejection
- Automatic reassignment after rejection or timeout
- Background worker for assignment timeout processing
- Prevention of repeated assignment attempts for the same task
- Dashboard metrics and activity logs

Technology Stack

Layer| Technology
Backend| Python, FastAPI
ORM| SQLAlchemy
Database| SQLite
Frontend| Next.js, React
API Documentation| Swagger / OpenAPI
Background Processing| Python asyncio

Project Structure

task-routing-system/
├── backend/
│   └── app/
│       ├── models/
│       ├── routers/
│       ├── services/
│       ├── database.py
│       ├── schemas.py
│       └── main.py
│
├── frontend/
│   ├── app/
│   └── lib/
│       └── api.ts
│
└── README.md

Getting Started

Backend

cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

Backend: http://localhost:8000

API documentation: http://localhost:8000/docs

Frontend

Open another terminal:

cd frontend
npm install
npm run dev

Frontend: http://localhost:3000

Assignment Workflow

1. Create a task with its required skills and priority.
2. The routing engine finds eligible contributors.
3. Contributors are evaluated using skill matching, workload, and capacity.
4. An assignment is created for the highest-ranked eligible contributor.
5. The contributor can accept or reject the assignment.
6. Rejected or timed-out assignments trigger reassignment.
7. Contributors already considered for a task are excluded from further attempts.
8. Dashboard metrics and activity logs reflect system activity.

Assignment Scoring

The routing engine evaluates eligible contributors using:

- Workload score: 50%
- Capacity score: 30%
- Skill score: 20%

Contributors who are unavailable, lack required skills, or have reached their capacity are excluded.

API Endpoints

Method| Endpoint| Purpose
GET| "/health"| Backend health
GET| "/tasks/"| List tasks
POST| "/tasks/"| Create a task
GET| "/contributors/"| List contributors
POST| "/contributors/"| Create a contributor
PUT| "/contributors/{id}"| Update a contributor
GET| "/assignments/"| List assignments
POST| "/assignments/auto/{task_id}"| Assign a specific task
POST| "/assignments/auto-next"| Assign the next eligible task
POST| "/assignments/{id}/accept"| Accept an assignment
POST| "/assignments/{id}/reject"| Reject an assignment
GET| "/dashboard/overview"| Dashboard overview

Current Status

Core routing, contributor eligibility, capacity enforcement, acceptance/rejection, timeout processing, reassignment, and dashboard functionality have been implemented and tested.

Further improvements can include automated tests, database migrations, authentication, and production deployment hardening.
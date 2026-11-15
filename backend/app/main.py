import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine, SessionLocal
from app import models
from app.routers import tasks, contributors, assignments, dashboard
from app.services.timeout_service import process_assignment_timeouts


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)


def run_timeout_cycle():
    """Run one timeout-processing cycle with its own database session."""

    db = SessionLocal()

    try:
        reassigned_tasks = process_assignment_timeouts(db)

        if reassigned_tasks:
            logger.info(
                "Automatically reassigned tasks: %s",
                reassigned_tasks
            )

    except Exception:
        db.rollback()
        logger.exception("Assignment timeout processing failed")

    finally:
        db.close()


async def timeout_worker():
    """Check for expired assignments once every second."""

    while True:
        await asyncio.to_thread(run_timeout_cycle)
        await asyncio.sleep(1)


@asynccontextmanager
async def lifespan(app: FastAPI):

    worker = asyncio.create_task(timeout_worker())

    logger.info("Assignment timeout worker started")

    try:
        yield

    finally:
        worker.cancel()

        try:
            await worker
        except asyncio.CancelledError:
            pass

        logger.info("Assignment timeout worker stopped")


app = FastAPI(
    title="Task Routing System",
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Task Routing System Backend Running"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


app.include_router(tasks.router)
app.include_router(contributors.router)
app.include_router(assignments.router)
app.include_router(dashboard.router)
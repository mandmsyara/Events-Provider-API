import asyncio
import logging
from contextlib import asynccontextmanager
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.routers.events import router as events_router
from app.api.routers.health import router as health_router
from app.core.config import settings
from app.middlewares.redirect import enforce_slash_middleware
from app.services.background_sync import sync_loop
from app.workers.outbox_worker import OutboxWorker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
)

logger = logging.getLogger(__name__)

if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        integrations=[FastApiIntegration()],
        environment=settings.environment,
        traces_sample_rate=0.0,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("app started")

    sync_task = asyncio.create_task(sync_loop())

    outbox_worker = OutboxWorker()
    outbox_task = asyncio.create_task(outbox_worker.run())

    try:
        yield
    finally:
        sync_task.cancel()
        outbox_task.cancel()

        for task in (sync_task, outbox_task):
            try:
                await task
            except asyncio.CancelledError:
                pass

        logger.info("app stopped")


app = FastAPI(lifespan=lifespan, redirect_slashes=False)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"detail": exc.errors()})


Instrumentator().instrument(app).expose(app)

app.middleware("http")(enforce_slash_middleware)

app.include_router(health_router)
app.include_router(events_router)

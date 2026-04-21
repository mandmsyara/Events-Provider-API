from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.routers.events import router as events_router
from app.api.routers.health import router as health_router
from app.middlewares.redirect import enforce_slash_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("app started")

    yield

    print("app stopped")


app = FastAPI(lifespan=lifespan, redirect_slashes=False)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"detail": exc.errors()})


Instrumentator().instrument(app).expose(app)

app.middleware("http")(enforce_slash_middleware)

app.include_router(health_router)
app.include_router(events_router)

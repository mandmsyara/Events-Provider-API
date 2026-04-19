from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.middlewares.redirect import enforce_slash_middleware
from app.api.routers.health import router as health_router
from app.api.routers.events import router as events_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("app started")

    yield

    print("app stopped")


app = FastAPI(lifespan=lifespan, redirect_slashes=False)

app.middleware("http")(enforce_slash_middleware)

app.include_router(health_router)
app.include_router(events_router)

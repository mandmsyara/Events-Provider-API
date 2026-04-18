from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.routers.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("app started")

    yield

    print("app stopped")


app = FastAPI(lifespan=lifespan)

app.include_router(health_router)

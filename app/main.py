from fastapi import FastAPI
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("app started")

    yield

    print("app stopped")


app = FastAPI(lifespan=lifespan)

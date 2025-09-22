from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers import ROUTERS as API_ROUTERS
from app.db.base import Base
from app.db.session import engine
from app.models import customer, product_order  # noqa: F401


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="FastAPI Application", lifespan=lifespan)

for router in API_ROUTERS:
    app.include_router(router)


@app.get("/")
def read_root():
    return {"message": "FastAPI에 오신 것을 환영합니다!"}

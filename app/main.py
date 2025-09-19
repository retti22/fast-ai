from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers import product_orders
from app.db.base import Base
from app.db.session import engine
from app.models import product_order  # noqa: F401


@asynccontextmanager
def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="FastAPI Application", lifespan=lifespan)

app.include_router(product_orders.router)


@app.get("/")
def read_root():
    return {"message": "FastAPI에 오신 것을 환영합니다!"}

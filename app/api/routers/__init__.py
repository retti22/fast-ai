from fastapi import APIRouter

from .customers import router as customers_router
from .product_orders import router as product_orders_router

ROUTERS: list[APIRouter] = [
    customers_router,
    product_orders_router,
]

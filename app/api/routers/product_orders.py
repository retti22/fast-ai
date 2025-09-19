from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.product_order import (
    ProductOrderCreate,
    ProductOrderRead,
    ProductOrderUpdate,
)
from app.services import product_order as service

router = APIRouter(prefix="/product-orders", tags=["product-orders"])


@router.post("/", response_model=ProductOrderRead, status_code=status.HTTP_201_CREATED)
def create_product_order(
    order_in: ProductOrderCreate, db: Session = Depends(get_db)
) -> ProductOrderRead:
    existing = service.get_order_by_number(db, order_in.order_number)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Order number already exists",
        )
    return service.create_order(db, order_in)


@router.get("/{order_id}", response_model=ProductOrderRead)
def read_product_order(order_id: int, db: Session = Depends(get_db)) -> ProductOrderRead:
    order = service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.get("/", response_model=list[ProductOrderRead])
def list_product_orders(
    skip: int = 0, limit: int = 50, db: Session = Depends(get_db)
) -> list[ProductOrderRead]:
    return list(service.list_orders(db, skip=skip, limit=limit))


@router.put("/{order_id}", response_model=ProductOrderRead)
def update_product_order(
    order_id: int, order_in: ProductOrderUpdate, db: Session = Depends(get_db)
) -> ProductOrderRead:
    order = service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return service.update_order(db, order, order_in)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_order(order_id: int, db: Session = Depends(get_db)) -> None:
    order = service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    service.delete_order(db, order)

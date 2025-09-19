from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.models.product_order import ProductOrder
from app.schemas.product_order import (
    ProductOrderCreate,
    ProductOrderRead,
    ProductOrderUpdate,
)


def create_order(db: Session, order_in: ProductOrderCreate) -> ProductOrder:
    order = ProductOrder(**order_in.model_dump())
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_order(db: Session, order_id: int) -> ProductOrder | None:
    return db.query(ProductOrder).filter(ProductOrder.id == order_id).first()


def get_order_by_number(db: Session, order_number: str) -> ProductOrder | None:
    return (
        db.query(ProductOrder)
        .filter(ProductOrder.order_number == order_number)
        .first()
    )


def list_orders(db: Session, skip: int = 0, limit: int = 50) -> Sequence[ProductOrder]:
    return db.query(ProductOrder).offset(skip).limit(limit).all()


def update_order(
    db: Session, order: ProductOrder, order_in: ProductOrderUpdate
) -> ProductOrder:
    for field, value in order_in.model_dump().items():
        setattr(order, field, value)
    db.commit()
    db.refresh(order)
    return order


def delete_order(db: Session, order: ProductOrder) -> None:
    db.delete(order)
    db.commit()

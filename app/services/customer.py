from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate


def create_customer(db: Session, customer_in: CustomerCreate) -> Customer:
    customer = Customer(**customer_in.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def get_customer(db: Session, customer_id: int) -> Customer | None:
    return db.query(Customer).filter(Customer.id == customer_id).first()


def get_customer_by_email(db: Session, email: str) -> Customer | None:
    return db.query(Customer).filter(Customer.email == email).first()


def list_customers(db: Session, skip: int = 0, limit: int = 50) -> Sequence[Customer]:
    return db.query(Customer).offset(skip).limit(limit).all()


def update_customer(
    db: Session, customer: Customer, customer_in: CustomerUpdate
) -> Customer:
    payload = customer_in.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in payload.items():
        setattr(customer, field, value)
    db.commit()
    db.refresh(customer)
    return customer


def delete_customer(db: Session, customer: Customer) -> None:
    db.delete(customer)
    db.commit()

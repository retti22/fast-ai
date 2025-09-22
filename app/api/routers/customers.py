from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate
from app.services import customer as service


router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("/", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
def create_customer(
    customer_in: CustomerCreate, db: Session = Depends(get_db)
) -> CustomerRead:
    existing = service.get_customer_by_email(db, customer_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists",
        )
    return service.create_customer(db, customer_in)


@router.get("/{customer_id}", response_model=CustomerRead)
def read_customer(customer_id: int, db: Session = Depends(get_db)) -> CustomerRead:
    customer = service.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer


@router.get("/", response_model=list[CustomerRead])
def list_customers(
    skip: int = 0, limit: int = 50, db: Session = Depends(get_db)
) -> list[CustomerRead]:
    return list(service.list_customers(db, skip=skip, limit=limit))


@router.put("/{customer_id}", response_model=CustomerRead)
def update_customer(
    customer_id: int, customer_in: CustomerUpdate, db: Session = Depends(get_db)
) -> CustomerRead:
    customer = service.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return service.update_customer(db, customer, customer_in)


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(customer_id: int, db: Session = Depends(get_db)) -> None:
    customer = service.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    service.delete_customer(db, customer)

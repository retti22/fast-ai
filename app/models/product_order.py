from sqlalchemy import Column, Integer, String

from app.db.base import Base


class ProductOrder(Base):
    __tablename__ = "product_order"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(64), unique=True, nullable=False, index=True)
    product_name = Column(String(255), nullable=False)
    shipping_address = Column(String(255), nullable=False)
    shipping_status = Column(String(50), nullable=False, default="pending")
    remark = Column(String(255), nullable=True)

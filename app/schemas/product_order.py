from pydantic import BaseModel, ConfigDict


class ProductOrderBase(BaseModel):
    order_number: str
    product_name: str
    shipping_address: str
    shipping_status: str
    remark: str | None = None


class ProductOrderCreate(ProductOrderBase):
    pass


class ProductOrderUpdate(BaseModel):
    order_number: str | None = None
    product_name: str | None = None
    shipping_address: str | None = None
    shipping_status: str | None = None
    remark: str | None = None


class ProductOrderRead(ProductOrderBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
